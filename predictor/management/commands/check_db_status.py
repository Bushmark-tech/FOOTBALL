from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Checks the production database connection and status'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== DATABASE DIAGNOSTIC REPORT ==='))
        self.stdout.write(f"Environment: {'PRODUCTION (Render)' if not settings.DEBUG else 'LOCAL/DEBUG'}")
        
        # 1. Check Configuration
        db_settings = settings.DATABASES['default']
        engine = db_settings['ENGINE']
        self.stdout.write(f"Configured Engine: {engine}")
        self.stdout.write(f"Database Name: {db_settings['NAME']}")
        
        if 'sqlite' in engine:
            self.stdout.write(self.style.WARNING("WARNING: You are using SQLite! Data WILL BE LOST on Render deploys."))
        elif 'postgresql' in engine:
            self.stdout.write(self.style.SUCCESS("SUCCESS: You are using PostgreSQL. Data persistence should be working."))
        
        # 2. Check Connection
        self.stdout.write("\nTesting Connection...")
        db_conn = connections['default']
        try:
            c = db_conn.cursor()
            self.stdout.write(self.style.SUCCESS("✓ Connection Successful!"))
        except OperationalError as e:
            self.stdout.write(self.style.ERROR(f"✗ Connection FAILED: {str(e)}"))
            return

        # 3. Check Data
        self.stdout.write("\nChecking Data stats...")
        User = get_user_model()
        try:
            user_count = User.objects.count()
            self.stdout.write(f"Total Registered Users: {user_count}")
            
            # Check for admin
            admin_exists = User.objects.filter(is_superuser=True).exists()
            if admin_exists:
                self.stdout.write(self.style.SUCCESS("✓ Admin user exists"))
            else:
                self.stdout.write(self.style.WARNING("! NO Admin user found"))
                
        except Exception as e:
             self.stdout.write(self.style.ERROR(f"Error reading data: {str(e)}"))

        self.stdout.write(self.style.SUCCESS('\n=== END REPORT ==='))
