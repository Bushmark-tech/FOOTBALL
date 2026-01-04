
import re
import os

file_path = 'templates/admin/users.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix split endif tag
# pattern: {% endif \n %}
content = re.sub(
    r'{% endif\s*\n\s*%}',
    '{% endif %}',
    content,
    flags=re.DOTALL
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Successfully processed {file_path}")
