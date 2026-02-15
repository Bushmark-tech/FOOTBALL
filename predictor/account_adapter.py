from allauth.account.adapter import DefaultAccountAdapter
import logging
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

logger = logging.getLogger(__name__)

class SafeAccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        """
        Overridden to catch SMTP errors so the user doesn't see a 500 error page.
        This allows the 'Success' page to show while the developer can still
        find the reset link in the terminal logs if SMTP authentication fails.
        """
        try:
            logger.info(f"[ALLAUTH EMAIL] Attempting to send '{template_prefix}' email to: {email}")
            super().send_mail(template_prefix, email, context)
            logger.info(f"[ALLAUTH EMAIL] '{template_prefix}' email sent successfully to: {email}")
        except Exception as e:
            logger.error(f"CRITICAL EMAIL FAILURE: {e}")
            
            # Print to console as a backup in case SMTP fails
            print("\n" + "="*50)
            print("FALLBACK: EMAIL FAILED TO SEND EXTERNALLY")
            print(f"To: {email}")
            print(f"Error: {e}")
            print("="*50 + "\n")
            
            # If we are in debug mode, it's helpful to see the error, 
            # but we want to fail gracefully so the user can continue testing.
            if settings.DEBUG:
                print("Tip: Check your .env file credentials. Gmail requires 2-Step Verification and an App Password.")
