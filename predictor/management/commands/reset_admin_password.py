"""
Management command to reset admin password or create new admin user.
Usage: python manage.py reset_admin_password
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Reset admin password or create new admin user'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Admin username (default: admin)'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='New password (will prompt if not provided)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@example.com',
            help='Admin email (default: admin@example.com)'
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options.get('password')
        email = options['email']
        
        # Try to find existing user
        try:
            user = User.objects.get(username=username)
            self.stdout.write(self.style.WARNING(f'Found existing user: {username}'))
            
            # Reset password
            if password:
                user.set_password(password)
            else:
                from getpass import getpass
                password = getpass('Enter new password: ')
                password2 = getpass('Confirm password: ')
                
                if password != password2:
                    self.stdout.write(self.style.ERROR('Passwords do not match!'))
                    return
                
                user.set_password(password)
            
            # Make sure user is superuser
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.save()
            
            self.stdout.write(self.style.SUCCESS(f'✓ Password reset for: {username}'))
            self.stdout.write(self.style.SUCCESS(f'✓ User is now superuser and staff'))
            
        except User.DoesNotExist:
            # Create new admin user
            self.stdout.write(self.style.WARNING(f'User {username} not found. Creating new admin user...'))
            
            if password:
                pass
            else:
                from getpass import getpass
                password = getpass('Enter password for new admin: ')
                password2 = getpass('Confirm password: ')
                
                if password != password2:
                    self.stdout.write(self.style.ERROR('Passwords do not match!'))
                    return
            
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            
            self.stdout.write(self.style.SUCCESS(f'✓ Created new admin user: {username}'))
            self.stdout.write(self.style.SUCCESS(f'✓ Email: {email}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ You can now login at /admin/ with:'))
        self.stdout.write(self.style.SUCCESS(f'   Username: {username}'))
        self.stdout.write(self.style.SUCCESS(f'   Password: (the one you just set)'))
