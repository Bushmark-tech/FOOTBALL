
import re
import os

file_path = 'templates/admin/predictions.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the backslashes introduced by the previous script
# {% if selected_outcome == \'Home\' %} -> {% if selected_outcome == 'Home' %}
content = content.replace(r"\'", "'")
content = content.replace(r'\"', '"')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Successfully processed {file_path}")
