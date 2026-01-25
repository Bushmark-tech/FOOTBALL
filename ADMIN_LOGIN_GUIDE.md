# Admin Login Guide - Football Prediction System

**Last Updated**: 2026-01-11

---

## 🔐 How to Login as Admin

Your system has **TWO admin interfaces**:

### 1. **Custom Admin Dashboard** (Recommended)
**URL**: `http://localhost:8000/admin/`

**Features**:
- Beautiful custom interface
- User management
- Prediction management
- Billing & subscriptions
- Analytics & reporting
- System control
- Data management

**Login**: Use your admin credentials (see below)

---

### 2. **Django System Admin** (For Database Management)
**URL**: `http://localhost:8000/system-core-database/`

**Features**:
- Direct database access
- Model management
- Built-in Django admin

**Login**: Same admin credentials

---

## 🚀 Quick Start

### Option 1: Use the Admin Management Script (Easiest)

```bash
# Run the admin management script
python manage_admin.py
```

**This script will**:
1. Check if admin user exists
2. Let you create a new admin
3. Let you reset admin password
4. Show you the login URLs

**Follow the prompts** to create or manage your admin user.

---

### Option 2: Use Django Command Line

#### Create New Admin User
```bash
python manage.py createsuperuser
```

**You'll be prompted for**:
- Username (e.g., `admin`)
- Email (e.g., `admin@example.com`)
- Password (enter twice)

#### Reset Admin Password
```bash
python manage.py changepassword <username>
```

---

## 📋 Default Admin Credentials

If you've just set up the system, you may have these defaults:

**Username**: `admin`  
**Password**: `admin123` (or what you set during creation)  
**Email**: `admin@example.com`

⚠️ **IMPORTANT**: Change the default password immediately in production!

---

## 🔍 Check if Admin Exists

### Method 1: Use the Script
```bash
python manage_admin.py
# Choose option 3 to check status
```

### Method 2: Django Shell
```bash
python manage.py shell
```

Then in the shell:
```python
from django.contrib.auth.models import User

# Check for admin users
admins = User.objects.filter(is_superuser=True)
for admin in admins:
    print(f"Username: {admin.username}")
    print(f"Email: {admin.email}")
    print(f"Active: {admin.is_active}")
```

Type `exit()` to leave the shell.

---

## 🛠️ Troubleshooting

### Problem: "No admin user found"

**Solution**: Create one using the script or command:
```bash
python manage_admin.py
# Choose option 1
```

Or:
```bash
python manage.py createsuperuser
```

---

### Problem: "Forgot admin password"

**Solution 1**: Use the script
```bash
python manage_admin.py
# Choose option 2
```

**Solution 2**: Use Django command
```bash
python manage.py changepassword admin
```

---

### Problem: "Admin page shows 404"

**Check**:
1. Is the server running?
   ```bash
   python manage.py runserver
   ```

2. Are you using the correct URL?
   - Custom admin: `http://localhost:8000/admin/`
   - Django admin: `http://localhost:8000/system-core-database/`

3. Check URL configuration in `predictor/urls.py` and `football_predictor/urls.py`

---

### Problem: "Login fails with correct credentials"

**Check**:
1. Is the user active?
   ```python
   # In Django shell
   from django.contrib.auth.models import User
   user = User.objects.get(username='admin')
   print(f"Active: {user.is_active}")
   print(f"Staff: {user.is_staff}")
   print(f"Superuser: {user.is_superuser}")
   ```

2. Make sure user is staff and superuser:
   ```python
   user.is_active = True
   user.is_staff = True
   user.is_superuser = True
   user.save()
   ```

---

### Problem: "Permission denied in admin"

**Solution**: Make sure user is superuser
```python
# In Django shell
from django.contrib.auth.models import User
user = User.objects.get(username='admin')
user.is_superuser = True
user.is_staff = True
user.save()
```

---

## 📱 Admin Dashboard Features

Once logged in to the custom admin (`/admin/`), you can:

### User Management
- View all users
- Edit user details
- Activate/deactivate users
- Manage subscriptions
- View user statistics

### Prediction Management
- View all predictions
- Filter by user, date, outcome
- Delete predictions
- View prediction statistics

### Billing & Subscriptions
- View all subscriptions
- Manage subscription plans
- View payment history
- Track revenue

### Analytics & Reporting
- System statistics
- User activity
- Prediction accuracy
- Revenue reports

### System Control
- Database status
- Cache management
- Model information
- System health

### Data Management
- Import data
- Export data
- Sync data
- View data statistics

---

## 🔒 Security Best Practices

### 1. Change Default Password
```bash
python manage.py changepassword admin
```

### 2. Use Strong Passwords
- At least 12 characters
- Mix of uppercase, lowercase, numbers, symbols
- Not a dictionary word

### 3. Disable Debug Mode in Production
```python
# settings.py
DEBUG = False
```

### 4. Restrict Admin Access
```python
# In settings.py
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

### 5. Use HTTPS in Production
- Install SSL certificate
- Force HTTPS redirect

### 6. Enable Two-Factor Authentication (Optional)
```bash
pip install django-otp
# Configure in settings.py
```

---

## 📝 Quick Commands Reference

```bash
# Create admin user
python manage.py createsuperuser

# Change password
python manage.py changepassword <username>

# Check admin status
python manage_admin.py

# Run server
python manage.py runserver

# Access Django shell
python manage.py shell

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

---

## 🌐 Admin URLs Summary

| Interface | URL | Purpose |
|-----------|-----|---------|
| Custom Admin Dashboard | `/admin/` | Main admin interface |
| Django System Admin | `/system-core-database/` | Database management |
| User Management | `/admin/users/` | Manage users |
| Predictions | `/admin/predictions/` | View predictions |
| Billing | `/admin/billing/` | Manage subscriptions |
| Analytics | `/admin/analytics/` | View reports |
| System | `/admin/system/` | System control |
| Data | `/admin/data/` | Data management |

---

## 💡 Tips

1. **Bookmark the admin URL** for quick access
2. **Use the custom admin** for most tasks (better UI)
3. **Use Django admin** only for direct database access
4. **Keep your password secure** - use a password manager
5. **Log out** when done, especially on shared computers
6. **Check logs** regularly in the admin dashboard
7. **Monitor system health** in the System section

---

## 🆘 Need Help?

### Can't Login?
1. Run `python manage_admin.py`
2. Choose option 1 to create admin
3. Or option 2 to reset password

### Server Not Running?
```bash
python manage.py runserver
```

### Database Issues?
```bash
python manage.py migrate
```

### Still Having Issues?
Check the logs:
- Console output when running server
- Django error pages (if DEBUG=True)
- Browser console (F12)

---

## 📚 Related Documentation

- **SYSTEM_DOCUMENTATION.md** - Complete system documentation
- **QUICK_REFERENCE.md** - Developer quick guide
- **ACTION_CHECKLIST.md** - System improvements
- **REVIEW_SUMMARY.md** - System review summary

---

## ✅ Checklist

Before using admin:
- [ ] Admin user created
- [ ] Password is secure (not default)
- [ ] Server is running (`python manage.py runserver`)
- [ ] Database is migrated (`python manage.py migrate`)
- [ ] You know the admin URL (`/admin/` or `/system-core-database/`)

---

**Happy administrating!** 🎉

If you have any questions, refer to this guide or run `python manage_admin.py` for interactive help.

---

*Last Updated: 2026-01-11*
