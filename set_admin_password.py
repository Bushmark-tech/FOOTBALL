"""
Quick script to set admin password to admin123
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from django.contrib.auth.models import User

# Set password
try:
    admin = User.objects.get(username='admin')
    admin.set_password('admin123')
    admin.save()
    
    print("\n" + "="*50)
    print("PASSWORD RESET SUCCESSFUL!")
    print("="*50)
    print("\nAdmin Login Credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\nLogin URLs:")
    print("  Custom Admin: http://localhost:8000/admin/")
    print("  Django Admin: http://localhost:8000/system-core-database/")
    print("\n" + "="*50)
    print("\nYou can now login to the admin dashboard!")
    print("="*50 + "\n")
    
except User.DoesNotExist:
    print("\nError: Admin user not found!")
except Exception as e:
    print(f"\nError: {e}")
