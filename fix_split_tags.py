import re

# Read the file
with open('templates/predictor/result.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and fix all split template tags
# Pattern: {{ followed by newline and whitespace, then content, then }}
pattern = r'\{\{\s*\r?\n\s*([^}]+?)\s*\}\}'

def fix_tag(match):
    # Get the content between {{ and }}
    inner = match.group(1)
    # Remove extra whitespace and newlines
    inner = ' '.join(inner.split())
    return f'{{{{ {inner} }}}}'

# Replace all occurrences
fixed_content = re.sub(pattern, fix_tag, content)

# Write back
with open('templates/predictor/result.html', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("Fixed all split template tags!")

# Count how many were fixed
original_count = len(re.findall(pattern, content))
print(f"Fixed {original_count} split tags")
