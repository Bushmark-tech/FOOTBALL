import os
import django
import sys
from django.core.mail import send_mail
from django.conf import settings

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

def test_email():
    print("Testing Email Configuration...")
    print(f"Backend: {settings.EMAIL_BACKEND}")
    print(f"Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
    print(f"User: {settings.EMAIL_HOST_USER}")
    print(f"TLS: {settings.EMAIL_USE_TLS}")
    
    try:
        send_mail(
            'Test Email from Football Predictor',
            'This is a test email to verify SMTP settings are working correctly.',
            settings.DEFAULT_FROM_EMAIL,
            [settings.EMAIL_HOST_USER], # Send to self
            fail_silently=False,
        )
        print("\n✅ SUCCESS: Test email sent successfully!")
        print(f"Check the inbox for: {settings.EMAIL_HOST_USER}")
    except Exception as e:
        print(f"\n❌ ERROR: Failed to send email.")
        print(f"Error details: {e}")

if __name__ == "__main__":
    test_email()
