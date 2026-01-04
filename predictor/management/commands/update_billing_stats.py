from django.core.management.base import BaseCommand
from predictor.models import BillingUsage, Prediction
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Update billing statistics for all users and sessions'

    def handle(self, *args, **options):
        self.stdout.write('Updating billing statistics...')
        
        # Update for authenticated users
        users = User.objects.all()
        user_count = 0
        for user in users:
            usage, created = BillingUsage.get_or_create_usage(user=user, session_key=None)
            if usage:
                usage.update_statistics()
                user_count += 1
        
        # Update for anonymous sessions
        session_keys = Prediction.objects.exclude(
            session_key__isnull=True
        ).exclude(
            session_key=''
        ).values_list('session_key', flat=True).distinct()
        
        session_count = 0
        for session_key in session_keys:
            usage, created = BillingUsage.get_or_create_usage(user=None, session_key=session_key)
            if usage:
                usage.update_statistics()
                session_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'[OK] Billing statistics updated successfully!\n'
                f'  - Users updated: {user_count}\n'
                f'  - Sessions updated: {session_count}\n'
                f'  - Total billing records: {BillingUsage.objects.count()}'
            )
        )

