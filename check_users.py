
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from django.contrib.auth.models import User

users = User.objects.all()
if users.exists():
    print("Existing users:")
    for u in users:
        print(f"- Username: {u.username}, Email: {u.email}, Staff: {u.is_staff}, Superuser: {u.is_superuser}")
else:
    print("No users found in the database.")
