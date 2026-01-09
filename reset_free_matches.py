"""
Reset free matches for testing - gives unlimited free matches
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.models import UserProfile
from django.contrib.auth.models import User

# Get all users
users = User.objects.all()

for user in users:
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Reset free matches
    profile.free_matches_used = 0
    profile.free_matches_limit = 999999  # Essentially unlimited for testing
    profile.save()
    
    print(f"✅ Reset free matches for {user.username}")
    print(f"   - Free matches: {profile.free_matches_used}/{profile.free_matches_limit}")
    print(f"   - Remaining: {profile.get_remaining_free_matches()}")

print("\n✅ All users now have unlimited free matches for testing!")
