
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from django.contrib.auth.models import User

username = 'admin'
email = 'admin@example.com'
password = 'admin123'

if User.objects.filter(username=username).exists():
    print(f"User {username} already exists. Resetting password.")
    user = User.objects.get(username=username)
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.is_active = True
    user.save()
    print(f"User {username} password reset to '{password}' and permissions updated.")
else:
    print(f"User {username} does not exist. Creating new superuser.")
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser {username} created with password '{password}'.")
