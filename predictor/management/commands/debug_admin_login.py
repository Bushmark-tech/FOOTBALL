"""
Debug command to check admin login issues.
Usage: python manage.py debug_admin_login <password>
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class Command(BaseCommand):
    help = 'Debug admin login'

    def add_arguments(self, parser):
        parser.add_argument('password', type=str, help='Password to test')

    def handle(self, *args, **options):
        password = options['password']
        username = 'admin'
        
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f"User found: {user.username}")
            self.stdout.write(f"Email: {user.email}")
            self.stdout.write(f"Is Active: {user.is_active}")
            self.stdout.write(f"Is Staff: {user.is_staff}")
            self.stdout.write(f"Is Superuser: {user.is_superuser}")
            
            # Check password
            is_correct = user.check_password(password)
            self.stdout.write(f"Password '{password}' correct? {is_correct}")
            
            if is_correct:
                # Try authenticate
                auth_user = authenticate(username=username, password=password)
                self.stdout.write(f"Authenticate returned user? {auth_user is not None}")
                if auth_user is None:
                    self.stdout.write(self.style.ERROR("! Authenticate failed despite correct password. Backend issue?"))
            else:
                self.stdout.write(self.style.ERROR("! Password incorrect in DB check."))
                
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User {username} does not exist!"))
