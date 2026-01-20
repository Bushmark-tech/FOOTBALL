
import re
import os

file_path = 'templates/admin/billing.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix spacing in if conditions
# {% if filter_type=='all' %} -> {% if filter_type == 'all' %}
content = re.sub(
    r'{%\s*if\s+([a-z_]+)==\'([a-z_]+)\'\s*%}',
    r"{% if \1 == '\2' %}",
    content
)

# Fix split variable
# {{ subscription.status|title \n }}
content = re.sub(
    r'\{\{\s*subscription\.status\|title\s*\n\s*\}\}',
    '{{ subscription.status|title }}',
    content,
    flags=re.DOTALL
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Successfully processed {file_path}")
