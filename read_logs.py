import os

log_path = r'c:\Users\user\Desktop\Football djang\Football-main\logs\django.log'
if os.path.exists(log_path):
    with open(log_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines[-15:]:
            print(line.strip())
else:
    print(f"Log not found at {log_path}")
