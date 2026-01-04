import os
import django
from django.contrib.auth.models import User

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

u = User.objects.get(username='james0082')
u.set_password('admin123')
u.is_active = True
u.save()
print(f"Password reset for james0082. Correct: {u.check_password('admin123')}")

u2, created = User.objects.get_or_create(username='admin')
u2.set_password('admin123')
u2.is_staff = True
u2.is_superuser = True
u2.save()
print(f"User 'admin' created/updated. Password: admin123")
