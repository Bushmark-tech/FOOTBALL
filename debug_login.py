
import os
import django
import sys

# Setup Django environment
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings_production')

try:
    django.setup()
except Exception as e:
    print(f"Error setting up Django: {e}")
    # Try falling back to local settings if production fails
    # This helps if running locally
    try:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'football_predictor.settings'
        django.setup()
    except:
        pass

from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

def check_login_capability(identifier, password_to_check=None):
    """
    Check if a user can theoretically login with the given identifier (username or email).
    Does NOT verify the password itself (can't reverse hash), but checks:
    1. If user exists
    2. If user is active
    3. Prints user details to help debug
    """
    print(f"\nChecking user with identifier: '{identifier}'")
    print("-" * 50)
    
    # Try finding by username OR email
    users = User.objects.filter(Q(username__iexact=identifier) | Q(email__iexact=identifier))
    
    if not users.exists():
        print(f"❌ User NOT FOUND")
        return

    for user in users:
        print(f"✅ FOUND User:")
        print(f"   • Username: {user.username}")
        print(f"   • Email:    {user.email}")
        print(f"   • Active:   {'Yes' if user.is_active else 'NO (Cannot login)'}")
        print(f"   • ID:       {user.id}")
        
        # Check backend if possible (info only)
        if hasattr(user, 'backend'):
            print(f"   • Backend:  {user.backend}")
            
        print(f"   • Has usable password: {user.has_usable_password()}")
        
        # If a password was provided to test (This won't actually login, just useful for scripts)
        if password_to_check:
            is_correct = user.check_password(password_to_check)
            print(f"   • Password Check ('{password_to_check}'): {'✅ CORRECT' if is_correct else '❌ INCORRECT'}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Check provided arguments
        identifier = sys.argv[1]
        password = sys.argv[2] if len(sys.argv) > 2 else None
        check_login_capability(identifier, password)
    else:
        # Default behavior: List all possible logins (username/email pairs)
        print("USAGE: python debug_login.py <username_or_email> [password_to_test]")
        print("\nListing all users and their login identifiers:")
        print("-" * 60)
        print(f"{'USERNAME':<25} | {'EMAIL':<30} | {'ACTIVE':<8} | {'STAFF'}")
        print("-" * 60)
        
        for u in User.objects.all().order_by('username'):
            active = "Yes" if u.is_active else "NO"
            staff = "Yes" if u.is_staff else "No"
            print(f"{u.username:<25} | {u.email:<30} | {active:<8} | {staff}")
