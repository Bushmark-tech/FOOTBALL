"""
Management command to manually verify user email addresses.
Usage: python manage.py verify_user <username_or_email>
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from predictor.models import UserProfile


class Command(BaseCommand):
    help = 'Manually verify a user email address'

    def add_arguments(self, parser):
        parser.add_argument('identifier', type=str, help='Username or email address')

    def handle(self, *args, **options):
        identifier = options['identifier']
        
        # Try to find user by username or email
        user = None
        try:
            if '@' in identifier:
                user = User.objects.get(email=identifier)
            else:
                user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User not found: {identifier}'))
            return
        
        # Get or create profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Check if already verified
        if profile.email_verified:
            self.stdout.write(self.style.WARNING(f'User {user.username} ({user.email}) is already verified'))
            return
        
        # Verify the user
        profile.email_verified = True
        profile.verification_token = None
        profile.token_created_at = None
        profile.save()
        
        # Activate user account
        if not user.is_active:
            user.is_active = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'✓ User account activated'))
        
        self.stdout.write(self.style.SUCCESS(f'✓ Email verified for: {user.username} ({user.email})'))
        self.stdout.write(self.style.SUCCESS(f'✓ User can now log in'))
