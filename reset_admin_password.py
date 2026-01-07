import os
import django
from django.conf import settings

# Manually configure settings if not already configured
if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings_production')
    django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("="*50)
print("RESETTING ADMIN PASSWORD")
print("="*50)

try:
    # 1. Reset 'admin' user
    u, created = User.objects.get_or_create(username='admin')
    u.set_password('adminpassword')
    u.email = 'admin@leon-football.com'
    u.is_staff = True
    u.is_superuser = True
    u.is_active = True
    u.save()
    action = "Created" if created else "Updated"
    print(f"✅ {action} user 'admin' with password 'adminpassword'")

except Exception as e:
    print(f"❌ Error: {e}")
