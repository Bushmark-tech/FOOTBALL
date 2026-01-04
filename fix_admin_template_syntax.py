
import re
import os

file_path = 'templates/admin/predictions.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix spacing in if conditions
# {% if selected_league==league %} -> {% if selected_league == league %}
content = re.sub(
    r'{%\s*if\s+selected_league==league\s*%}',
    '{% if selected_league == league %}',
    content
)

# {% if selected_outcome=='Home' %} -> {% if selected_outcome == 'Home' %}
content = re.sub(
    r'{%\s*if\s+selected_outcome==\'(Home|Draw|Away)\'\s*%}',
    r'{% if selected_outcome == \'\1\' %}',
    content
)

# Also check for double quotes just in case
content = re.sub(
    r'{%\s*if\s+selected_outcome==\"(Home|Draw|Away)\"\s*%}',
    r'{% if selected_outcome == \"\1\" %}',
    content
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Successfully processed {file_path}")
