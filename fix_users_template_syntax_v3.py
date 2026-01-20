
import os
import re

file_path = r'c:\Users\user\Desktop\Footballb2\FOOTBALL\templates\admin\users.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace assignments in template tags causing syntax errors
# pattern: {% if filter_type=='value' %}
# we want: {% if filter_type == 'value' %}

def replacer(match):
    # match.group(1) is 'filter_type'
    # match.group(2) is 'value'
    return f"{{% if {match.group(1)} == '{match.group(2)}' %}}"

# Regex to find these patterns. 
# It looks for {% if filter_type=='some_value' %}
# We need to be careful with quotes.
new_content = re.sub(r"{%\s*if\s+(filter_type)=='([^']+)'\s*%}", replacer, content)

if content == new_content:
    print("No changes made by regex. Checking for manual strings...")
    # Fallback to direct replacement if regex fails for some reason or simple string replace is safer
    replacements = [
        ("filter_type=='all'", "filter_type == 'all'"),
        ("filter_type=='active'", "filter_type == 'active'"),
        ("filter_type=='inactive'", "filter_type == 'inactive'"),
        ("filter_type=='subscribed'", "filter_type == 'subscribed'"),
        ("filter_type=='staff'", "filter_type == 'staff'")
    ]
    for old, new in replacements:
        if old in new_content:
            print(f"Replacing {old} with {new}")
            new_content = new_content.replace(old, new)

if content != new_content:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully fixed filter_type syntax errors.")
else:
    print("Content matched expectations or no patterns found (which is unexpected given the error).")

