"""
Custom Password Reset View with Email Logging
"""
import logging
from django.contrib.auth.views import PasswordResetView
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


class CustomPasswordResetView(PasswordResetView):
    """
    Custom password reset view that logs email sending attempts
    """
    
    def form_valid(self, form):
        """
        Override to add logging before sending email
        """
        email = form.cleaned_data.get('email')
        domain = self.extra_email_context.get('domain', 'unknown')
        site_name = self.extra_email_context.get('site_name', 'unknown')
        logger.info(f"[PASSWORD RESET] Attempting to send password reset email to: {email} (Domain: {domain}, Site: {site_name})")
        
        try:
            # Call the parent form_valid which sends the email
            response = super().form_valid(form)
            logger.info(f"[PASSWORD RESET] Email sent successfully to: {email}")
            return response
        except Exception as e:
            logger.error(f"[PASSWORD RESET] Failed to send email to {email}: {str(e)}", exc_info=True)
            # Re-raise to show error to user
            raise
