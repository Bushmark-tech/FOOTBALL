import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

def test_smtp():
    host = os.getenv('EMAIL_HOST')
    port = int(os.getenv('EMAIL_PORT'))
    user = os.getenv('EMAIL_HOST_USER')
    password = os.getenv('EMAIL_HOST_PASSWORD')
    
    print(f"Testing SMTP for {user} at {host}:{port}...")
    
    try:
        server = smtplib.SMTP(host, port)
        server.set_debuglevel(1)
        server.starttls()
        server.login(user, password)
        print("\n✅ Successfully authenticated!")
        server.quit()
    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")

if __name__ == "__main__":
    test_smtp()
