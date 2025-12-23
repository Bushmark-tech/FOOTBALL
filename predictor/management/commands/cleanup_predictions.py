"""
Management command to clean up old predictions for scalability.

Usage:
    python manage.py cleanup_predictions
    python manage.py cleanup_predictions --archive-days 60
    python manage.py cleanup_predictions --delete-archived-days 365
    python manage.py cleanup_predictions --dry-run
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from predictor.models import Prediction


class Command(BaseCommand):
    help = 'Archive and delete old predictions to maintain database performance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--archive-days',
            type=int,
            default=90,
            help='Archive predictions older than this many days (default: 90)'
        )
        parser.add_argument(
            '--delete-archived-days',
            type=int,
            default=180,
            help='Delete archived predictions older than this many days (default: 180)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned up without actually doing it'
        )

    def handle(self, *args, **options):
        archive_days = options['archive_days']
        delete_days = options['delete_archived_days']
        dry_run = options['dry_run']

        self.stdout.write(self.style.SUCCESS('Starting prediction cleanup...'))
        self.stdout.write(f'Archive predictions older than: {archive_days} days')
        self.stdout.write(f'Delete archived predictions older than: {delete_days} days')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        # Get counts before cleanup
        total_predictions = Prediction.objects.count()
        active_predictions = Prediction.objects.filter(is_archived=False).count()
        archived_predictions = Prediction.objects.filter(is_archived=True).count()

        self.stdout.write('\nCurrent Statistics:')
        self.stdout.write(f'  Total predictions: {total_predictions}')
        self.stdout.write(f'  Active predictions: {active_predictions}')
        self.stdout.write(f'  Archived predictions: {archived_predictions}')

        # Archive old predictions
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Step 1: Archiving old predictions...')
        
        if not dry_run:
            archived_count = Prediction.cleanup_old_predictions(days_to_keep=archive_days)
            self.stdout.write(self.style.SUCCESS(f'✓ Archived {archived_count} predictions'))
        else:
            # Count what would be archived
            from datetime import timedelta
            cutoff_date = timezone.now() - timedelta(days=archive_days)
            would_archive = Prediction.objects.filter(
                prediction_date__lt=cutoff_date,
                is_archived=False
            ).count()
            self.stdout.write(self.style.WARNING(f'Would archive {would_archive} predictions'))

        # Delete very old archived predictions
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Step 2: Deleting very old archived predictions...')
        
        if not dry_run:
            deleted_count = Prediction.delete_archived_predictions(days_archived=delete_days)
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {deleted_count} archived predictions'))
        else:
            # Count what would be deleted
            from datetime import timedelta
            cutoff_date = timezone.now() - timedelta(days=delete_days)
            would_delete = Prediction.objects.filter(
                is_archived=True,
                archived_date__lt=cutoff_date
            ).count()
            self.stdout.write(self.style.WARNING(f'Would delete {would_delete} archived predictions'))

        # Show final statistics
        if not dry_run:
            final_total = Prediction.objects.count()
            final_active = Prediction.objects.filter(is_archived=False).count()
            final_archived = Prediction.objects.filter(is_archived=True).count()

            self.stdout.write('\n' + '='*50)
            self.stdout.write('Final Statistics:')
            self.stdout.write(f'  Total predictions: {final_total} (was {total_predictions})')
            self.stdout.write(f'  Active predictions: {final_active} (was {active_predictions})')
            self.stdout.write(f'  Archived predictions: {final_archived} (was {archived_predictions})')
            
            space_saved = total_predictions - final_total
            if space_saved > 0:
                self.stdout.write(self.style.SUCCESS(f'\n✓ Freed up {space_saved} database records'))

        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('✓ Cleanup completed successfully!'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nThis was a dry run. Run without --dry-run to apply changes.'))

