"""
Email verification utility functions for Football Predictor
"""
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


def send_verification_email(user, request):
    """
    Send email verification link to user.
    
    Args:
        user: User object
        request: HTTP request object (for building absolute URL)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Get or create user profile
        profile = user.profile
        
        # Generate verification token
        token = profile.generate_verification_token()
        
        # Build verification URL
        verification_url = request.build_absolute_uri(
            reverse('predictor:verify_email', kwargs={'token': token})
        )
        
        # Email subject and message
        subject = 'Verify Your Email - Football Predictor Pro'
        message = f"""
Hello {user.username},

Thank you for registering with Football Predictor Pro!

Please verify your email address by clicking the link below:

{verification_url}

This link will expire in 24 hours.

If you didn't create this account, please ignore this email.

Best regards,
Football Predictor Pro Team
"""
        
        html_message = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c3e50;">Welcome to Football Predictor Pro!</h2>
        
        <p>Hello <strong>{user.username}</strong>,</p>
        
        <p>Thank you for registering with Football Predictor Pro!</p>
        
        <p>Please verify your email address by clicking the button below:</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{verification_url}" 
               style="background-color: #3498db; color: white; padding: 12px 30px; 
                      text-decoration: none; border-radius: 5px; display: inline-block;">
                Verify Email Address
            </a>
        </div>
        
        <p style="color: #7f8c8d; font-size: 14px;">
            Or copy and paste this link into your browser:<br>
            <a href="{verification_url}">{verification_url}</a>
        </p>
        
        <p style="color: #e74c3c; font-size: 14px;">
            <strong>Note:</strong> This link will expire in 24 hours.
        </p>
        
        <p>If you didn't create this account, please ignore this email.</p>
        
        <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 30px 0;">
        
        <p style="color: #95a5a6; font-size: 12px;">
            Best regards,<br>
            <strong>Football Predictor Pro Team</strong>
        </p>
    </div>
</body>
</html>
"""
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Verification email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {e}")
        return False


def send_welcome_email(user):
    """
    Send welcome email after successful verification.
    
    Args:
        user: User object
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        subject = 'Welcome to Football Predictor Pro!'
        message = f"""
Hello {user.username},

Your email has been successfully verified!

You can now enjoy:
✓ 3 Free AI-powered match predictions
✓ Access to historical data and team statistics
✓ Multi-match prediction mode
✓ Detailed prediction analytics

Start making predictions now: {settings.SITE_URL}

Best regards,
Football Predictor Pro Team
"""
        
        html_message = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #27ae60;">✓ Email Verified Successfully!</h2>
        
        <p>Hello <strong>{user.username}</strong>,</p>
        
        <p>Your email has been successfully verified! Welcome to Football Predictor Pro.</p>
        
        <div style="background-color: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #2c3e50;">What You Get:</h3>
            <ul style="list-style: none; padding: 0;">
                <li style="padding: 8px 0;">✓ <strong>3 Free Predictions</strong> - AI-powered match analysis</li>
                <li style="padding: 8px 0;">✓ <strong>Historical Data</strong> - Access to team statistics</li>
                <li style="padding: 8px 0;">✓ <strong>Multi-Match Mode</strong> - Predict multiple matches at once</li>
                <li style="padding: 8px 0;">✓ <strong>Detailed Analytics</strong> - In-depth prediction insights</li>
            </ul>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{settings.SITE_URL}/predict/" 
               style="background-color: #27ae60; color: white; padding: 12px 30px; 
                      text-decoration: none; border-radius: 5px; display: inline-block;">
                Start Predicting Now
            </a>
        </div>
        
        <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 30px 0;">
        
        <p style="color: #95a5a6; font-size: 12px;">
            Best regards,<br>
            <strong>Football Predictor Pro Team</strong>
        </p>
    </div>
</body>
</html>
"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=True,  # Don't fail if welcome email doesn't send
        )
        
        logger.info(f"Welcome email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {e}")
        return False
