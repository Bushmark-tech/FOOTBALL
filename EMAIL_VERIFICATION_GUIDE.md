# Email Verification Implementation Guide

## Overview
Email verification has been implemented for the Football Predictor Pro application to ensure users can only log in with verified email addresses.

## Changes Made

### 1. Database Model Updates (`predictor/models.py`)
Added email verification fields to `UserProfile`:
- `email_verified` (Boolean, default=False)
- `verification_token` (CharField, unique)
- `token_created_at` (DateTimeField)

Added helper methods:
- `generate_verification_token()` - Creates a secure token
- `is_token_valid()` - Checks if token is still valid (24 hours)

### 2. Email Utilities (`predictor/email_utils.py`)
Created email sending functions:
- `send_verification_email(user, request)` - Sends verification link
- `send_welcome_email(user)` - Sends welcome email after verification

### 3. Authentication Views (`predictor/auth_views.py`)
Updated:
- `register_view()` - Now creates inactive users and sends verification email
- `login_view()` - Checks email verification before allowing login
- Added `verify_email(request, token)` - Handles email verification

### 4. URL Configuration (`predictor/urls.py`)
Added:
- `path('verify-email/<str:token>/', auth_views.verify_email, name='verify_email')`

## Required Configuration

### Email Settings (add to `settings.py` or `.env`)
```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'  # Your Gmail address
EMAIL_HOST_PASSWORD = 'your-app-password'  # Gmail App Password
DEFAULT_FROM_EMAIL = 'Football Predictor Pro <your-email@gmail.com>'
SITE_URL = 'https://football-2-v5fy.onrender.com'  # Your site URL
```

### Gmail App Password Setup
1. Go to Google Account settings
2. Enable 2-Factor Authentication
3. Go to Security > App Passwords
4. Generate a new app password for "Mail"
5. Use this password in `EMAIL_HOST_PASSWORD`

## Database Migration

Run these commands to apply the changes:
```bash
python manage.py makemigrations predictor
python manage.py migrate
```

## User Flow

### Registration:
1. User registers with @gmail.com email
2. Account created with `is_active=False`
3. Verification email sent with unique token link
4. User redirected to login with message to check email

### Email Verification:
1. User clicks verification link in email
2. Token validated (must be < 24 hours old)
3. `email_verified` set to `True`
4. `is_active` set to `True`
5. Welcome email sent
6. User redirected to login

### Login:
1. User enters email/username and password
2. System checks if email is verified
3. If not verified: Login blocked with message
4. If verified: Login successful

## Security Features
- Tokens expire after 24 hours
- Tokens are single-use (cleared after verification)
- Users cannot log in until email is verified
- Secure token generation using `secrets.token_urlsafe(32)`

## Testing Locally

For local testing without email:
1. Set `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`
2. Verification emails will print to console
3. Copy the verification link from console and open in browser

## Production Deployment

1. Add email settings to Render environment variables
2. Run migrations on Render
3. Test registration flow
4. Monitor email delivery logs

## Troubleshooting

### Emails not sending:
- Check Gmail App Password is correct
- Verify EMAIL_HOST_USER matches the Gmail account
- Check Render logs for email errors
- Ensure SITE_URL is correct for link generation

### Users can't verify:
- Check token expiry (24 hours)
- Verify URL pattern is correct
- Check database for verification_token value

### Login still blocked after verification:
- Check `email_verified` field in database
- Check `is_active` field in User model
- Clear browser cache and try again
