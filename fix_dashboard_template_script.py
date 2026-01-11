
import os

file_path = r'c:\Users\user\Desktop\Footballb2\FOOTBALL\templates\admin\dashboard_base.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# The pattern to replace
old_pattern = '{% if user.is_superuser %}Administrator{% else %}Staff Member{% endif\n                        %}'
new_pattern = '{% if user.is_superuser %}Administrator{% else %}Staff Member{% endif %}'

# Try finding it with universal newlines in mind
if old_pattern not in content:
    print("Exact pattern not found trying variations...")
    # Try normalized variation just in case
    old_pattern_v2 = '{% if user.is_superuser %}Administrator{% else %}Staff Member{% endif\n                        %}'
    # We might need to handle \r\n
    old_pattern_crlf = '{% if user.is_superuser %}Administrator{% else %}Staff Member{% endif\r\n                        %}'
    
    if old_pattern_crlf in content:
        print("Found CRLF pattern")
        content = content.replace(old_pattern_crlf, new_pattern)
    elif old_pattern in content:
        print("Found LF pattern (should have been caught)")
        content = content.replace(old_pattern, new_pattern)
    else:
        print("Could not find pattern to replace!")
        # Let's print what we see around the area
        idx = content.find('Administrator{% else %}Staff Member{% endif')
        if idx != -1:
            print("Context around find:")
            print(repr(content[idx:idx+100]))
        else:
            print("Could not find start of block.")
        exit(1)
else:
    print("Found exact pattern.")
    content = content.replace(old_pattern, new_pattern)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully wrote file.")
