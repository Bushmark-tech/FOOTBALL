
import re
import os

file_path = r"C:\Users\user\Desktop\FOOTBALL-PREDICTION-APP-main\templates\predictor\result.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Debug: Print matches before
print("Scanning for multi-line tags...")

# 1. Fix the big IF for double chance
# We look for "{% if 'Win or Draw' ... %}" possibly spanning multiple lines
pattern1 = re.compile(r"\{%\s*if\s*'Win or Draw' in final_prediction.*?\12' in final_prediction\s*%\ সারাদেশ", re.DOTALL)
# Actually, let's make the regex more permissive but specific enough
# "{% if 'Win or Draw' in final_prediction ... '12' in final_prediction ... %}"
pattern1 = re.compile(r"\{%\s*if\s*'Win or Draw' in final_prediction.*?%\ সারাদেশ", re.DOTALL)

replacement1 = "{% if 'Win or Draw' in final_prediction or 'Win or Away' in final_prediction or '/ Draw' in final_prediction or '1X' in final_prediction or 'X2' in final_prediction or '12' in final_prediction %}"

match1 = pattern1.search(content)
if match1:
    print("Found Pattern 1 (Double Chance)")
    content = content.replace(match1.group(0), replacement1)
else:
    print("Pattern 1 NOT found (might be already fixed or slightly different)")

# 2. Fix the ELIF Home
# "{% elif 'Home' in final_prediction ... %}"
pattern2 = re.compile(r"\{%\s*elif\s*'Home' in final_prediction.*?Win'\s*%\ সারাদেশ", re.DOTALL)
replacement2 = "{% elif 'Home' in final_prediction or final_prediction == 'Home' or final_prediction == 'Home Team Win' %}"

match2 = pattern2.search(content)
if match2:
    print("Found Pattern 2 (Home Win)")
    content = content.replace(match2.group(0), replacement2)
else:
    print("Pattern 2 NOT found")

# 3. Fix the ELIF Away
# "{% elif 'Away' in final_prediction ... %}"
pattern3 = re.compile(r"\{%\s*elif\s*'Away' in final_prediction.*?Win'\s*%\ সারাদেশ", re.DOTALL)
replacement3 = "{% elif 'Away' in final_prediction or final_prediction == 'Away' or final_prediction == 'Away Team Win' %}"

match3 = pattern3.search(content)
if match3:
    print("Found Pattern 3 (Away Win)")
    content = content.replace(match3.group(0), replacement3)
else:
    print("Pattern 3 NOT found")


with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Finished processing result.html")
