# Bot Protection & Email Verification Security Fix

## Problem Identified

From the logs at **2026-02-17 10:11:35**, a bot was able to:
1. Access `/accounts/signup/` (django-allauth signup page)
2. Create an account with email `tradingfacesaz@gmail.com`
3. Receive verification email but **not verify it**
4. Attempt to login without email verification

## Root Cause

The application had `ACCOUNT_EMAIL_VERIFICATION = 'optional'` which allowed users to:
- Create accounts without verifying their email
- Login without email verification
- Potentially consume free matches without valid email addresses

## Security Fixes Implemented

### 1. **Mandatory Email Verification** ✅
**File**: `football_predictor/settings.py` (Line 229)

**Change**:
```python
# Before
ACCOUNT_EMAIL_VERIFICATION = 'optional'

# After
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # Require email verification before login
```

**Impact**:
- Users MUST verify their email before they can login
- Bots cannot login without access to the email inbox
- Google OAuth users are still auto-verified (Google already verified their email)

---

### 2. **Rate Limiting on Signup** ✅
**File**: `predictor/allauth_views.py` (NEW FILE)

**Implementation**:
```python
@method_decorator(ratelimit(key='ip', rate='3/h', block=True), name='dispatch')
class RateLimitedSignupView(SignupView):
    """Limits signups to 3 per hour per IP address"""
```

**Impact**:
- Prevents mass bot signups from the same IP
- Limits to 3 signups per hour per IP address
- Returns HTTP 403 if rate limit exceeded

---

### 3. **Disposable Email Blocking** ✅
**File**: `predictor/account_adapter.py`

**Enhancement**:
```python
def clean_email(self, email):
    """Validate email and block disposable email providers"""
    email = super().clean_email(email)
    
    # Block disposable email domains
    from predictor.constants import DISPOSABLE_EMAIL_DOMAINS
    domain = email.split('@')[1].lower() if '@' in email else ''
    
    if domain in DISPOSABLE_EMAIL_DOMAINS:
        logger.warning(f"Blocked disposable email signup attempt: {email}")
        raise ValueError("Temporary or disposable email addresses are not allowed.")
    
    return email
```

**Impact**:
- Blocks temporary/disposable email services (mailinator, guerrillamail, etc.)
- Forces users to use legitimate email addresses
- Prevents throwaway account creation

---

### 4. **Enhanced Signup Tracking** ✅
**File**: `predictor/account_adapter.py`

**Enhancement**:
```python
def save_user(self, request, user, form, commit=True):
    """Save user with additional tracking information"""
    # Track IP and device for security
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    # Log signup attempt
    logger.info(f"New allauth signup: {user.email} from IP: {ip}")
```

**Impact**:
- Logs all signup attempts with IP addresses
- Helps identify bot patterns
- Provides audit trail for security analysis

---

### 5. **Honeypot Protection** ✅
**File**: `predictor/allauth_views.py`

**Implementation**:
```python
def form_valid(self, form):
    """Additional validation before signup"""
    # Honeypot check
    if self.request.POST.get('website'):
        logger.warning(f"Bot signup blocked via honeypot: {form.cleaned_data.get('email')}")
        # Silently redirect without creating account
        return redirect('account_signup')
    
    return super().form_valid(form)
```

**Impact**:
- Catches bots that auto-fill all form fields
- Invisible to human users
- Silently blocks bot signups

---

## How It Works Now

### For Regular Email Signups:
1. User visits `/accounts/signup/`
2. Rate limit check (3/hour per IP) ✅
3. Honeypot field check ✅
4. Email validation (no disposable emails) ✅
5. Account created but **INACTIVE** ✅
6. Verification email sent ✅
7. User clicks verification link
8. Account activated ✅
9. User can now login ✅

### For Google OAuth Signups:
1. User clicks "Sign in with Google"
2. Google authenticates user
3. Google returns **verified** email
4. Account created and **ACTIVE** immediately ✅
5. User logged in (no verification needed) ✅

---

## Testing the Fix

### Test 1: Bot Signup Attempt
```bash
# Bot tries to signup 4 times in an hour
curl -X POST https://leon-football.com/accounts/signup/ \
  -d "email=bot@example.com&password1=test123&password2=test123"

# Expected: First 3 succeed, 4th returns HTTP 403 (rate limited)
```

### Test 2: Disposable Email
```bash
# Try to signup with disposable email
curl -X POST https://leon-football.com/accounts/signup/ \
  -d "email=test@mailinator.com&password1=test123&password2=test123"

# Expected: Error message "Temporary or disposable email addresses are not allowed."
```

### Test 3: Login Without Verification
```bash
# Create account
POST /accounts/signup/ with valid email

# Try to login immediately (without verifying email)
POST /login/ with credentials

# Expected: Error message "Please verify your email before logging in"
```

---

## Monitoring

### Log Patterns to Watch:

**Successful Protection**:
```
WARNING:predictor.account_adapter:Blocked disposable email signup attempt: test@mailinator.com
WARNING:predictor.allauth_views:Bot signup blocked via honeypot: bot@example.com
```

**Suspicious Activity**:
```
INFO:predictor.account_adapter:New allauth signup: user@example.com from IP: 1.2.3.4
INFO:predictor.account_adapter:New allauth signup: user2@example.com from IP: 1.2.3.4
INFO:predictor.account_adapter:New allauth signup: user3@example.com from IP: 1.2.3.4
# Same IP, multiple signups = potential bot
```

---

## Additional Recommendations

### 1. Add CAPTCHA (Optional)
For even stronger protection, consider adding Google reCAPTCHA:
```python
# settings.py
INSTALLED_APPS += ['captcha']

# allauth_views.py
from captcha.fields import ReCaptchaField
```

### 2. Email Domain Whitelist (Optional)
For enterprise use, allow only specific domains:
```python
ALLOWED_EMAIL_DOMAINS = ['company.com', 'partner.com']
```

### 3. Monitor Failed Login Attempts
Track repeated failed logins from same IP:
```python
# After 5 failed attempts, temporarily block IP
```

---

## Files Modified

1. ✅ `football_predictor/settings.py` - Mandatory email verification
2. ✅ `predictor/account_adapter.py` - Disposable email blocking + tracking
3. ✅ `predictor/allauth_views.py` - Rate limiting + honeypot (NEW FILE)
4. ✅ `football_predictor/urls.py` - Custom signup view integration

---

## Deployment Checklist

- [ ] Test email verification flow in staging
- [ ] Verify Google OAuth still works (should bypass verification)
- [ ] Test rate limiting (3 signups/hour per IP)
- [ ] Confirm disposable email blocking works
- [ ] Monitor logs for bot activity
- [ ] Update user documentation about email verification requirement

---

## Summary

**Before**: Bots could create accounts and potentially login without email verification.

**After**: 
- ✅ Email verification is **mandatory** for all email/password signups
- ✅ Rate limiting prevents mass bot signups (3/hour per IP)
- ✅ Disposable emails are blocked
- ✅ Honeypot catches automated bots
- ✅ All signups are logged with IP addresses
- ✅ Google OAuth users still have seamless experience

**Result**: Significantly reduced bot abuse while maintaining good user experience for legitimate users.
