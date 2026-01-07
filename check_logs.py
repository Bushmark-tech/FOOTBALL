import os

# Check multiple possible locations for the log file
possible_paths = [
    os.path.join(os.getcwd(), 'logs', 'django.log'),
    os.path.join('/opt/render/project/src/logs', 'django.log'),
    os.path.join('/var/log', 'django.log'),
]

log_file = None
for path in possible_paths:
    if os.path.exists(path):
        log_file = path
        break

if not log_file:
    log_file = possible_paths[0] # Default for printing


print(f"Checking log file at: {log_file}")

if os.path.exists(log_file):
    print("CHECK: Log file found. Last 50 lines:")
    print("-" * 50)
    try:
        with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
            for line in lines[-50:]:
                print(line.strip())
    except Exception as e:
        print(f"ERROR: Error reading log file: {e}")
else:
    print("ERROR: Log file NOT found.")
    if os.path.exists(os.path.join(os.getcwd(), 'logs')):
         print("   'logs' directory exists.")
    else:
         print("   'logs' directory does NOT exist.")

print("-" * 50)
