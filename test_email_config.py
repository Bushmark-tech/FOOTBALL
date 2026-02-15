"""
Test email configuration and send a test email
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail

print("=" * 80)
print("EMAIL CONFIGURATION CHECK")
print("=" * 80)
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print("=" * 80)

if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
    print("\n⚠️  WARNING: Using console backend - emails will NOT be sent!")
    print("Set EMAIL_BACKEND environment variable to: django.core.mail.backends.smtp.EmailBackend")
elif not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
    print("\n⚠️  WARNING: EMAIL_HOST_USER or EMAIL_HOST_PASSWORD not set!")
else:
    print("\n✅ Email configuration looks good!")
    
    # Try to send a test email
    try:
        print("\nAttempting to send test email...")
        send_mail(
            subject='Test Email from Football Predictor',
            message='This is a test email to verify SMTP configuration.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        print("✅ Test email sent successfully!")
        print(f"Check inbox: {settings.EMAIL_HOST_USER}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        print(f"Error type: {type(e).__name__}")
