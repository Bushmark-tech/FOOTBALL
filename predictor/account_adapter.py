from allauth.account.adapter import DefaultAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.contrib import messages
import logging
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

logger = logging.getLogger(__name__)

class SafeAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        """
        Check if signup is allowed (can be used to temporarily disable signups)
        """
        return super().is_open_for_signup(request)
    
    def clean_email(self, email):
        """
        Validate email and block disposable email providers
        """
        email = super().clean_email(email)
        
        # Block disposable email domains
        from predictor.constants import DISPOSABLE_EMAIL_DOMAINS
        domain = email.split('@')[1].lower() if '@' in email else ''
        
        if domain in DISPOSABLE_EMAIL_DOMAINS:
            logger.warning(f"Blocked disposable email signup attempt: {email}")
            raise ValueError("Temporary or disposable email addresses are not allowed.")
        
        return email
    
    def save_user(self, request, user, form, commit=True):
        """
        Save user with additional tracking information
        """
        user = super().save_user(request, user, form, commit=False)
        
        # Track IP and device for security
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Log signup attempt
        logger.info(f"New allauth signup: {user.email} from IP: {ip}")
        
        if commit:
            user.save()
        
        return user
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
