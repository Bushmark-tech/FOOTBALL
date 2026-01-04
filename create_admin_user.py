
import os
import sys
import django

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_superuser():
    User = get_user_model()
    username = 'admin'
    email = 'admin@example.com'
    password = 'adminpassword'

    if not User.objects.filter(username=username).exists():
        print(f"Creating superuser: {username}")
        try:
            User.objects.create_superuser(username, email, password)
            print(f"Superuser '{username}' created successfully.")
            print(f"Email: {email}")
            print(f"Password: {password}")
        except Exception as e:
            print(f"Error creating superuser: {e}")
    else:
        print(f"Superuser '{username}' already exists.")
        # Optional: Reset password if known
        # u = User.objects.get(username=username)
        # u.set_password(password)
        # u.save()
        # print(f"Password reset for '{username}' to '{password}'")

if __name__ == '__main__':
    create_superuser()
