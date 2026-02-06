import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from django.contrib.auth.models import User
from predictor.models import UserProfile

username = 'cdickerson4'
try:
    user = User.objects.get(username=username)
    print(f"User: {user.username} (ID: {user.id})")
    
    try:
        profile = user.profile
        print(f"Profile: Exists")
        print(f"Free Matches Limit: {profile.free_matches_limit}")
        print(f"Free Matches Used: {profile.free_matches_used}")
    except User.profile.RelatedObjectDoesNotExist:
        print("Profile: MISSING")
        # Create it
        UserProfile.objects.create(user=user)
        print("Profile: Created new profile with default settings")

except User.DoesNotExist:
    print(f"User {username} not found")
