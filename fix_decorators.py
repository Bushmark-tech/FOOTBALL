import os

file_path = r'c:\Users\user\Desktop\Football djang\Football-main\predictor\admin_views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_content = content.replace("@login_required(login_url='predictor:login')\n@user_passes_test(is_admin)", "@admin_required")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Replacement complete.")
