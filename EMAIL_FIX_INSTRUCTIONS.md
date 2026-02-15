# Email Configuration Fix - Deployment Instructions

## Problem Summary
The password reset emails are not being sent on production (leon-football.com). The logs show the password reset flow is working correctly (user submits form, gets redirected to "done" page), but emails are not arriving in users' inboxes.

## Root Cause
The environment variables for email configuration are set in Render's dashboard, but Django may not be loading them properly, or there's an SMTP authentication issue.

## Changes Made

### 1. Added Email Configuration Logging
- **File**: `football_predictor/settings.py`
- **File**: `football_predictor/settings_production.py`
- **Purpose**: Log email configuration on startup to verify environment variables are loaded

The logs will now show:
```
================================================================================
EMAIL CONFIGURATION (Production)
================================================================================
EMAIL_BACKEND: django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST: smtp.gmail.com
EMAIL_PORT: 587
EMAIL_USE_TLS: True
EMAIL_HOST_USER: wesildaventures88@gmail.com
EMAIL_HOST_PASSWORD: SET (16 chars)
DEFAULT_FROM_EMAIL: Football Predictor <noreply@leon-football.com>
================================================================================
```

### 2. Diagnostic Script
- **File**: `test_email_config.py`
- **Purpose**: Test email configuration locally or on production

## Next Steps - Deploy and Check

### Step 1: Deploy to Render
```bash
git add .
git commit -m "Add email configuration logging for debugging"
git push origin main
```

### Step 2: Check Render Logs
After deployment, go to your Render dashboard and check the logs for:

1. **Email Configuration Output** - Look for the "EMAIL CONFIGURATION" section
2. **Check for warnings**:
   - "WARNING: Using console email backend" - means SMTP is not configured
   - "WARNING: EMAIL_HOST_USER or EMAIL_HOST_PASSWORD not set" - means credentials are missing

### Step 3: Verify Environment Variables in Render

Make sure these are set in Render Dashboard → Environment:
- `EMAIL_BACKEND` = `django.core.mail.backends.smtp.EmailBackend`
- `EMAIL_HOST` = `smtp.gmail.com`
- `EMAIL_PORT` = `587`
- `EMAIL_USE_TLS` = `True`
- `EMAIL_HOST_USER` = `wesildaventures88@gmail.com`
- `EMAIL_HOST_PASSWORD` = `wsis test hbzr hwux` (your Gmail App Password)
- `DEFAULT_FROM_EMAIL` = `Football Predictor <wesildaventures88@gmail.com>`

### Step 4: Check for SMTP Errors

If the configuration looks correct but emails still don't send, check Render logs for SMTP errors like:
- `SMTPAuthenticationError` - Wrong credentials
- `SMTPServerDisconnected` - Network/firewall issue
- `SMTPException` - General SMTP error

## Common Issues and Solutions

### Issue 1: Gmail App Password Not Working
**Solution**: Generate a new App Password:
1. Go to https://myaccount.google.com/apppasswords
2. Generate new password for "Mail"
3. Update `EMAIL_HOST_PASSWORD` in Render

### Issue 2: Gmail Blocking Sign-in
**Solution**: 
1. Check Gmail security settings
2. Enable "Less secure app access" (if available)
3. Or use a different SMTP service like SendGrid

### Issue 3: Environment Variables Not Loading
**Solution**:
1. Verify variables are set in Render dashboard (not just in render.yaml)
2. Restart the service after setting variables
3. Check the startup logs for the EMAIL CONFIGURATION output

## Testing Email on Production

Once deployed, you can test by:
1. Going to https://leon-football.com/password_reset/
2. Entering an email address
3. Checking the Render logs for:
   - Email configuration output
   - Any SMTP errors
   - Success message (if email sent)

## Alternative: Use SendGrid (Recommended for Production)

If Gmail continues to have issues, consider using SendGrid:

1. Sign up at https://sendgrid.com (free tier: 100 emails/day)
2. Get API key
3. Update Render environment variables:
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.sendgrid.net
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=apikey
   EMAIL_HOST_PASSWORD=<your-sendgrid-api-key>
   DEFAULT_FROM_EMAIL=Football Predictor <noreply@leon-football.com>
   ```

## Contact
If issues persist after checking the logs, provide:
1. The EMAIL CONFIGURATION output from Render logs
2. Any SMTP error messages
3. The full log output when a user requests password reset
