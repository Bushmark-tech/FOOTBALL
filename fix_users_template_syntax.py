
import re
import os

file_path = 'templates/admin/users.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix spacing in if conditions
# {% if filter_type=='all' %} -> {% if filter_type == 'all' %}
content = re.sub(
    r'{%\s*if\s+filter_type==\'([a-z_]+)\'\s*%}',
    r"{% if filter_type == '\1' %}",
    content
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Successfully processed {file_path}")
