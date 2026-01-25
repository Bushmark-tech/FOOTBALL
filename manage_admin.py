"""
Quick script to check admin status and create/reset admin user
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from django.contrib.auth.models import User

def check_admin():
    """Check if admin user exists"""
    admins = User.objects.filter(is_superuser=True)
    
    print("\n" + "="*50)
    print("ADMIN USER STATUS")
    print("="*50)
    
    if admins.exists():
        print(f"\n[OK] Found {admins.count()} admin user(s):\n")
        for admin in admins:
            print(f"  Username: {admin.username}")
            print(f"  Email: {admin.email}")
            print(f"  Active: {admin.is_active}")
            print(f"  Staff: {admin.is_staff}")
            print(f"  Superuser: {admin.is_superuser}")
            print(f"  Last login: {admin.last_login}")
            print()
    else:
        print("\n[!] No admin users found!")
        print("\nYou need to create an admin user.")
    
    print("="*50)
    return admins.exists()

def create_admin():
    """Create a new admin user"""
    print("\n" + "="*50)
    print("CREATE ADMIN USER")
    print("="*50)
    
    username = input("\nEnter admin username (default: admin): ").strip() or "admin"
    email = input("Enter admin email (default: admin@example.com): ").strip() or "admin@example.com"
    password = input("Enter admin password (default: admin123): ").strip() or "admin123"
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"\n[!] User '{username}' already exists!")
        update = input("Update to admin/superuser? (y/n): ").strip().lower()
        if update == 'y':
            user = User.objects.get(username=username)
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.set_password(password)
            user.save()
            print(f"\n[OK] User '{username}' updated to admin!")
        else:
            print("\n[X] Cancelled.")
            return
    else:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"\n[OK] Admin user '{username}' created successfully!")
    
    print("\n" + "="*50)
    print("LOGIN CREDENTIALS")
    print("="*50)
    print(f"\nUsername: {username}")
    print(f"Password: {password}")
    print(f"Email: {email}")
    print("\n" + "="*50)

def reset_admin_password():
    """Reset admin password"""
    print("\n" + "="*50)
    print("RESET ADMIN PASSWORD")
    print("="*50)
    
    username = input("\nEnter admin username: ").strip()
    
    try:
        user = User.objects.get(username=username)
        new_password = input("Enter new password: ").strip()
        user.set_password(new_password)
        user.save()
        print(f"\n[OK] Password reset successfully for '{username}'!")
        print(f"\nNew credentials:")
        print(f"  Username: {username}")
        print(f"  Password: {new_password}")
    except User.DoesNotExist:
        print(f"\n[X] User '{username}' not found!")
    
    print("\n" + "="*50)

def main():
    print("\n" + "="*50)
    print("FOOTBALL PREDICTION - ADMIN MANAGEMENT")
    print("="*50)
    
    # Check current admin status
    has_admin = check_admin()
    
    print("\nOptions:")
    print("  1. Create new admin user")
    print("  2. Reset admin password")
    print("  3. Check admin status only")
    print("  4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        create_admin()
    elif choice == '2':
        reset_admin_password()
    elif choice == '3':
        pass  # Already checked above
    elif choice == '4':
        print("\nExiting...")
    else:
        print("\n[X] Invalid choice!")
    
    print("\n" + "="*50)
    print("ADMIN LOGIN URLS")
    print("="*50)
    print("\nCustom Admin Dashboard:")
    print("  http://localhost:8000/admin/")
    print("\nDjango Admin (System Core):")
    print("  http://localhost:8000/system-core-database/")
    print("\n" + "="*50)

if __name__ == '__main__':
    main()
