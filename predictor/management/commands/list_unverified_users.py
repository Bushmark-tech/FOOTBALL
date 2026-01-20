"""
Management command to list all unverified users.
Usage: python manage.py list_unverified_users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from predictor.models import UserProfile


class Command(BaseCommand):
    help = 'List all users with unverified email addresses'

    def handle(self, *args, **options):
        # Get all user profiles where email is not verified
        unverified_profiles = UserProfile.objects.filter(email_verified=False)
        
        if not unverified_profiles.exists():
            self.stdout.write(self.style.SUCCESS('✓ All users are verified!'))
            return
        
        self.stdout.write(self.style.WARNING(f'\nFound {unverified_profiles.count()} unverified users:\n'))
        self.stdout.write(self.style.WARNING('=' * 80))
        
        for profile in unverified_profiles:
            user = profile.user
            status = "ACTIVE" if user.is_active else "INACTIVE"
            
            self.stdout.write(f'\nUsername: {user.username}')
            self.stdout.write(f'Email:    {user.email}')
            self.stdout.write(f'Status:   {status}')
            self.stdout.write(f'Joined:   {user.date_joined.strftime("%Y-%m-%d %H:%M")}')
            
            if profile.verification_token:
                if profile.is_token_valid():
                    self.stdout.write(self.style.SUCCESS('Token:    Valid (not expired)'))
                else:
                    self.stdout.write(self.style.ERROR('Token:    Expired'))
            else:
                self.stdout.write('Token:    None')
            
            self.stdout.write('-' * 80)
        
        self.stdout.write(f'\n{self.style.WARNING("To verify a user manually, run:")}')
        self.stdout.write(f'{self.style.SUCCESS("python manage.py verify_user <username_or_email>")}')
