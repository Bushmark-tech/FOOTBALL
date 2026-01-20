# Admin Password Reset Guide

## Quick Methods to Reset Admin Password

### Method 1: Using Custom Command (EASIEST)
```bash
# Interactive (will prompt for password)
python manage.py reset_admin_password

# With specific username
python manage.py reset_admin_password --username admin

# Non-interactive (specify password directly)
python manage.py reset_admin_password --username admin --password newpassword123
```

### Method 2: Using Django's Built-in Command
```bash
# Change password for existing admin user
python manage.py changepassword admin

# It will prompt:
# Password: [enter new password]
# Password (again): [confirm password]
```

### Method 3: Create New Superuser
```bash
python manage.py createsuperuser

# It will prompt for:
# Username: [enter username]
# Email: [enter email]
# Password: [enter password]
# Password (again): [confirm password]
```

### Method 4: Django Shell (Advanced)
```bash
python manage.py shell
```

Then run:
```python
from django.contrib.auth.models import User

# Find admin user
admin = User.objects.get(username='admin')

# Set new password
admin.set_password('your_new_password')
admin.save()

print("✓ Password reset successfully!")
```

### Method 5: Direct Database Reset (Emergency)
```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User

# Delete old admin (if exists)
try:
    User.objects.get(username='admin').delete()
except:
    pass

# Create fresh admin
admin = User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='admin123'  # Change this!
)

print("✓ New admin created!")
print("Username: admin")
print("Password: admin123")
```

## Production (Render) Password Reset

### Option 1: Using Render Shell
1. Go to Render Dashboard
2. Select your service
3. Click "Shell" tab
4. Run:
```bash
python manage.py reset_admin_password --username admin --password YourNewPassword123
```

### Option 2: Using Environment Variables
1. Add to Render environment variables:
```
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
```

2. Create initialization script in `manage.py` or startup:
```python
import os
from django.contrib.auth.models import User

username = os.environ.get('ADMIN_USERNAME', 'admin')
password = os.environ.get('ADMIN_PASSWORD')

if password:
    try:
        admin = User.objects.get(username=username)
        admin.set_password(password)
        admin.save()
    except User.DoesNotExist:
        User.objects.create_superuser(username, 'admin@example.com', password)
```

## Common Scenarios

### Scenario 1: Forgot Admin Password
**Solution:**
```bash
python manage.py reset_admin_password
# Enter new password when prompted
```

### Scenario 2: Admin User Doesn't Exist
**Solution:**
```bash
python manage.py createsuperuser
# Follow prompts to create new admin
```

### Scenario 3: Need Multiple Admin Users
**Solution:**
```bash
# Create additional admins
python manage.py createsuperuser --username admin2
python manage.py createsuperuser --username admin3
```

### Scenario 4: Reset Password on Production
**Solution:**
```bash
# On Render Shell
python manage.py reset_admin_password --username admin --password NewSecurePass123
```

## Security Best Practices

### Strong Password Requirements
- Minimum 8 characters
- Mix of uppercase and lowercase
- Include numbers
- Include special characters
- Example: `Admin@2026!Secure`

### Recommended Passwords for Different Environments

**Local Development:**
```
Username: admin
Password: admin123
```

**Staging:**
```
Username: admin
Password: Staging@2026!
```

**Production:**
```
Username: admin
Password: [Use strong password generator]
Example: Pr0d@2026!Ft8aLl#
```

## Troubleshooting

### Issue: "User matching query does not exist"
**Solution:**
```bash
# Create new admin
python manage.py createsuperuser
```

### Issue: "Password is too similar to username"
**Solution:**
- Use a more complex password
- Don't use "admin" as password for "admin" user

### Issue: "This password is too common"
**Solution:**
- Use a unique password
- Add numbers and special characters

### Issue: Can't Access Admin Panel After Reset
**Check:**
1. Is user active? `user.is_active = True`
2. Is user staff? `user.is_staff = True`
3. Is user superuser? `user.is_superuser = True`

**Fix:**
```python
from django.contrib.auth.models import User
admin = User.objects.get(username='admin')
admin.is_active = True
admin.is_staff = True
admin.is_superuser = True
admin.save()
```

## Quick Reference

| Task | Command |
|------|---------|
| Reset password (interactive) | `python manage.py reset_admin_password` |
| Reset password (direct) | `python manage.py reset_admin_password --password newpass` |
| Change existing password | `python manage.py changepassword admin` |
| Create new admin | `python manage.py createsuperuser` |
| Check admin exists | `python manage.py shell` → `User.objects.filter(is_superuser=True)` |

## Current Admin Credentials

After running the reset command, your credentials will be:

**Local Development:**
- URL: `http://localhost:8000/admin/`
- Username: `admin` (or what you specified)
- Password: (what you just set)

**Production:**
- URL: `https://football-2-v5fy.onrender.com/admin/`
- Username: `admin` (or what you specified)
- Password: (what you set via Render shell)

## Emergency Access

If you're completely locked out:

1. **Delete database** (local only):
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

2. **Create new admin via code**:
Add to `manage.py`:
```python
if __name__ == "__main__":
    # Auto-create admin on first run
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
```

## Notes

- Always use strong passwords in production
- Change default passwords immediately
- Don't commit passwords to git
- Use environment variables for production
- Keep admin credentials secure
