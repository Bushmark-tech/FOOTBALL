import re

with open('templates/predictor/result.html', encoding='utf-8') as f:
    lines = f.readlines()

split_tags = []
for i, line in enumerate(lines, 1):
    # Check if line has {{ but not }}
    if '{{' in line and '}}' not in line:
        # Get next few lines to see the complete tag
        context = ''.join(lines[i-1:min(i+2, len(lines))])
        split_tags.append((i, line.strip(), context))

print(f"Found {len(split_tags)} split template tags:\n")
for line_num, line_text, context in split_tags:
    print(f"Line {line_num}:")
    print(f"  {line_text[:120]}")
    print(f"  Context: {context[:200]}")
    print()
