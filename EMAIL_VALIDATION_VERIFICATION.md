# Email Validation & Verification System

## 📧 Overview
Your Football Prediction App has a comprehensive email validation and verification system to ensure user authenticity and security.

---

## 🔐 Email Validation (Registration)

### **Restriction: Gmail Only**
- **Location:** `predictor/auth_views.py` (Lines 246-249)
- **Rule:** Only `@gmail.com` email addresses are allowed
- **Code:**
```python
if not email or not email.strip().lower().endswith('@gmail.com'):
    messages.error(request, 'Registration is restricted to valid Google (@gmail.com) email addresses only.')
    return render(request, 'predictor/register.html')
```

### **Unique Email Check**
- **Location:** `predictor/auth_views.py` (Lines 251-254)
- **Rule:** Each email can only be registered once
- **Code:**
```python
if User.objects.filter(email=email).exists():
    messages.error(request, 'This email address is already registered. Please login.')
    return render(request, 'predictor/register.html')
```

---

## ✅ Email Verification System

### **How It Works:**

1. **User Registers** → System creates account with `email_verified=False`

2. **Verification Email Sent** → User receives email with verification link
   - **Token Generated:** Secure 32-character URL-safe token
   - **Token Expiry:** 24 hours
   - **Email Template:** Professional HTML email with button

3. **User Clicks Link** → Token is validated
   - Checks if token exists
   - Checks if token is still valid (< 24 hours)
   - Checks if already verified

4. **Email Verified** → Account activated
   - Sets `email_verified=True`
   - Activates user account (`is_active=True`)
   - Clears verification token
   - Sends welcome email

---

## 📝 Database Fields

### **UserProfile Model** (`predictor/models.py`)
```python
email_verified = models.BooleanField(default=False)
verification_token = models.CharField(max_length=100, blank=True, null=True, unique=True)
token_created_at = models.DateTimeField(blank=True, null=True)
```

---

## 📨 Email Templates

### **1. Verification Email**
- **Subject:** "Verify Your Email - Football Predictor Pro"
- **Sender:** `DEFAULT_FROM_EMAIL` (configured in settings)
- **Content:**
  - Welcome message
  - Verification button/link
  - 24-hour expiry notice
  - Professional HTML design

### **2. Welcome Email** (After Verification)
- **Subject:** "Welcome to Football Predictor Pro!"
- **Content:**
  - Confirmation of successful verification
  - **1 Free Prediction** (updated ✓)
  - Feature highlights
  - Call-to-action button

---

## 🔧 Key Functions

### **1. `send_verification_email(user, request)`**
- **Location:** `predictor/email_utils.py`
- **Purpose:** Sends verification email to new users
- **Returns:** `True` if successful, `False` otherwise

### **2. `send_welcome_email(user)`**
- **Location:** `predictor/email_utils.py`
- **Purpose:** Sends welcome email after verification
- **Returns:** `True` if successful, `False` otherwise

### **3. `verify_email(request, token)`**
- **Location:** `predictor/auth_views.py` (Lines 634-685)
- **Purpose:** Handles email verification via token
- **Validates:**
  - Token exists
  - Token not expired (< 24 hours)
  - Email not already verified

---

## ⚙️ Email Configuration

### **Settings** (`football_predictor/settings.py`)
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Production
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = 'Football Predictor <noreply@football-predictor.com>'
```

### **Required Environment Variables:**
- `EMAIL_HOST_USER` - Your Gmail address
- `EMAIL_HOST_PASSWORD` - Gmail App Password (not regular password)

---

## 🛡️ Security Features

1. **Token Security:**
   - 32-character URL-safe random token
   - Unique constraint in database
   - Automatically cleared after use

2. **Token Expiry:**
   - 24-hour validity window
   - Prevents old tokens from being used

3. **Email Uniqueness:**
   - One email = one account
   - Prevents duplicate registrations

4. **Gmail Restriction:**
   - Only `@gmail.com` addresses allowed
   - Reduces spam and fake accounts

---

## 📊 Admin Features

### **Django Admin Panel:**
- View email verification status
- Manually verify users
- See verification token status
- Filter by verified/unverified users

### **Management Commands:**
1. **List Unverified Users:**
   ```bash
   python manage.py list_unverified_users
   ```

2. **Manually Verify User:**
   ```bash
   python manage.py verify_user <username>
   ```

---

## 🔄 User Flow

```
Registration
    ↓
Email Validation (@gmail.com only)
    ↓
Account Created (email_verified=False)
    ↓
Verification Email Sent (24h token)
    ↓
User Clicks Link
    ↓
Token Validated
    ↓
Email Verified (email_verified=True)
    ↓
Welcome Email Sent
    ↓
User Can Login & Get 1 Free Prediction
```

---

## ✅ Current Status (Updated)

- ✅ Gmail-only registration enforced
- ✅ Email uniqueness validated
- ✅ Verification email system active
- ✅ 24-hour token expiry
- ✅ Welcome email updated to show **1 Free Prediction**
- ✅ Professional HTML email templates
- ✅ Admin panel integration
- ✅ Security best practices implemented

---

## 🚀 Testing Locally

To test email verification locally:

1. **Option 1: Console Backend (Development)**
   ```python
   EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
   ```
   Emails will print to console instead of sending

2. **Option 2: Gmail SMTP (Production-like)**
   - Create Gmail App Password
   - Set environment variables:
     ```
     EMAIL_HOST_USER=your-email@gmail.com
     EMAIL_HOST_PASSWORD=your-app-password
     ```

---

## 📌 Notes

- Email verification is **optional** by default (`ACCOUNT_EMAIL_VERIFICATION = 'optional'`)
- Users can login immediately after registration
- Verification provides additional security and trust
- Failed email sends are logged but don't block registration
