import os

log_file = os.path.join(os.getcwd(), 'logs', 'django.log')

print(f"Checking log file at: {log_file}")

if os.path.exists(log_file):
    print("✅ Log file found. Last 50 lines:")
    print("-" * 50)
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-50:]:
                print(line.strip())
    except Exception as e:
        print(f"❌ Error reading log file: {e}")
else:
    print("❌ Log file NOT found.")
    if os.path.exists(os.path.join(os.getcwd(), 'logs')):
         print("   'logs' directory exists.")
    else:
         print("   'logs' directory does NOT exist.")

print("-" * 50)
