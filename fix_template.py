
path = r"c:\Users\user\Desktop\FOOTBALL-PREDICTION-APP-main\templates\admin\dashboard_base.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix the specific split tag
old_tag = """{% if user.is_superuser %}Administrator{% else %}Staff Member{% endif
                        %}"""
new_tag = """{% if user.is_superuser %}Administrator{% else %}Staff Member{% endif %}"""

# Normalize line endings just in case
content = content.replace(old_tag, new_tag)

# Also try a more generic replace if whitespace is different
import re
pattern = r"{% if user\.is_superuser %}Administrator{% else %}Staff Member{% endif\s+%}"
content = re.sub(pattern, "{% if user.is_superuser %}Administrator{% else %}Staff Member{% endif %}", content)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("File updated.")
