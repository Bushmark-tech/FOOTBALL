# User Verification Guide

## Overview
This guide explains how to verify users manually so they can log in without email verification.

## Methods to Verify Users

### Method 1: Django Admin Panel (Easiest)
1. Log in to Django admin: `https://football-2-v5fy.onrender.com/admin/`
2. Go to **Predictor** → **User profiles**
3. You'll see a column "Email Status" showing ✓ Verified or ✗ Not Verified
4. Select the users you want to verify (checkbox on left)
5. From the "Action" dropdown, select **"✓ Verify selected users (bypass email)"**
6. Click "Go"
7. Users are now verified and can log in!

### Method 2: Command Line (Local/Server)
```bash
# Verify a single user by username
python manage.py verify_user john_doe

# Verify a user by email
python manage.py verify_user user@gmail.com

# List all unverified users
python manage.py list_unverified_users
```

### Method 3: Django Shell
```python
python manage.py shell

from django.contrib.auth.models import User
from predictor.models import UserProfile

# Find user
user = User.objects.get(username='john_doe')  # or email='user@gmail.com'

# Get profile
profile = user.profile

# Verify
profile.email_verified = True
profile.verification_token = None
profile.token_created_at = None
profile.save()

# Activate account
user.is_active = True
user.save()

print(f"✓ {user.username} verified!")
```

### Method 4: Bulk Verify All Users (Emergency)
```python
python manage.py shell

from predictor.models import UserProfile
from django.contrib.auth.models import User

# Verify all unverified users
profiles = UserProfile.objects.filter(email_verified=False)
for profile in profiles:
    profile.email_verified = True
    profile.verification_token = None
    profile.token_created_at = None
    profile.save()
    
    # Activate user
    if not profile.user.is_active:
        profile.user.is_active = True
        profile.user.save()

print(f"✓ Verified {profiles.count()} users!")
```

## Checking User Status

### In Admin Panel
- Go to **Predictor** → **User profiles**
- Look at "Email Status" column
- Green ✓ = Verified
- Red ✗ = Not Verified

### Via Command Line
```bash
# List all unverified users
python manage.py list_unverified_users

# Output shows:
# - Username
# - Email
# - Account status (ACTIVE/INACTIVE)
# - Join date
# - Token validity
```

### Via Django Shell
```python
from predictor.models import UserProfile

# Count unverified users
unverified = UserProfile.objects.filter(email_verified=False).count()
print(f"Unverified users: {unverified}")

# List them
for profile in UserProfile.objects.filter(email_verified=False):
    print(f"{profile.user.username} - {profile.user.email}")
```

## Common Scenarios

### Scenario 1: User Says "I Didn't Get Verification Email"
**Solution:**
1. Go to admin panel
2. Find the user in User profiles
3. Select them and use "Verify selected users" action
4. Tell user they can now log in

### Scenario 2: User Registered But Can't Login
**Check:**
1. Is email verified? (Admin → User profiles → Email Status)
2. Is account active? (Admin → Users → Active checkbox)

**Fix:**
- Use admin action to verify
- Or use command: `python manage.py verify_user username`

### Scenario 3: Verification Link Expired
**Solution:**
- Manually verify using any method above
- User can then log in immediately

### Scenario 4: Want to Disable Email Verification Temporarily
**Option 1: Verify all existing users**
```bash
python manage.py shell
# Run bulk verify script from Method 4
```

**Option 2: Modify registration (not recommended)**
- Edit `predictor/auth_views.py`
- In `register_view`, set `is_active=True` instead of `False`
- Set `email_verified=True` when creating profile
- This bypasses verification entirely

## Admin Panel Features

### User Profile Admin Shows:
- ✓/✗ Email verification status
- Token validity (if exists)
- Free matches used/limit
- Payment method
- Join date

### Available Actions:
1. **Verify selected users** - Bypass email verification
2. **Reset free quota** - Reset prediction count to 0
3. **Grant 30 days free access** - Give free subscription

## Troubleshooting

### User Still Can't Login After Verification
Check:
1. Is `email_verified = True`?
2. Is `user.is_active = True`?
3. Is password correct?

Fix:
```python
user = User.objects.get(username='username')
user.is_active = True
user.save()
user.profile.email_verified = True
user.profile.save()
```

### Can't Find User in Admin
- Check spelling
- Search by email instead of username
- User might not have a profile (create one):
```python
from predictor.models import UserProfile
UserProfile.objects.get_or_create(user=user)
```

## Best Practices

1. **For Testing**: Manually verify test users
2. **For Production**: Let email verification work
3. **For Support**: Use admin panel to help users
4. **For Bulk Operations**: Use management commands

## Quick Reference

| Task | Command |
|------|---------|
| Verify one user | `python manage.py verify_user username` |
| List unverified | `python manage.py list_unverified_users` |
| Admin verify | Admin → User profiles → Select → Verify action |
| Check status | Admin → User profiles → Email Status column |

## Security Note

Manual verification bypasses the email confirmation step. Only verify users you trust or who have contacted you directly for support.
