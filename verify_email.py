import os
import django
from django.core.mail import send_mail
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

def test_email():
    print("Testing Email Configuration...")
    print(f"Host: {settings.EMAIL_HOST}")
    print(f"Port: {settings.EMAIL_PORT}")
    print(f"User: {settings.EMAIL_HOST_USER}")
    
    subject = 'Leon Football - Email Test'
    message = 'This is a test email to verify your SMTP configuration.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ['wasikeonesmus980@gmail.com']
    
    try:
        sent = send_mail(subject, message, from_email, recipient_list)
        if sent:
            print("SUCCESS: Email sent successfully!")
        else:
            print("FAILURE: Email was not sent (unknown reason).")
    except Exception as e:
        import traceback
        print(f"CRITICAL ERROR: {e}")
        traceback.print_exc()
        print("\nTroubleshooting Tips:")
        print("1. Ensure 'App Passwords' are enabled in your Google Account.")
        print("2. Verify that 2nd Step Verification is ON.")
        print("3. Check if the password in .env is correct (no spaces).")

if __name__ == '__main__':
    test_email()
