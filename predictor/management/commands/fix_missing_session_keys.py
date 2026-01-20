from django.core.management.base import BaseCommand
from predictor.models import Prediction
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Fix predictions with missing session_key by archiving old ones or assigning to a default session'

    def add_arguments(self, parser):
        parser.add_argument(
            '--archive-old',
            action='store_true',
            help='Archive predictions older than 30 days that have no session_key',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to consider as "old" (default: 30)',
        )

    def handle(self, *args, **options):
        self.stdout.write('Checking for predictions with missing session_key...')
        
        # Find predictions without session_key
        predictions_without_session = Prediction.objects.filter(
            session_key__isnull=True,
            user__isnull=True,
            is_archived=False
        )
        
        total_count = predictions_without_session.count()
        self.stdout.write(f'Found {total_count} predictions without session_key or user')
        
        if total_count == 0:
            self.stdout.write(self.style.SUCCESS('[OK] No predictions with missing session_key found'))
            return
        
        if options['archive_old']:
            # Archive old predictions
            cutoff_date = timezone.now() - timedelta(days=options['days'])
            old_predictions = predictions_without_session.filter(
                prediction_date__lt=cutoff_date
            )
            old_count = old_predictions.count()
            
            if old_count > 0:
                old_predictions.update(
                    is_archived=True,
                    archived_date=timezone.now()
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'[OK] Archived {old_count} old predictions (older than {options["days"]} days)'
                    )
                )
            
            remaining = predictions_without_session.filter(is_archived=False).count()
            if remaining > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'[WARNING] {remaining} recent predictions still have no session_key. '
                        f'These may be from before session tracking was implemented.'
                    )
                )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'[INFO] Found {total_count} predictions without session_key.\n'
                    f'Run with --archive-old to archive predictions older than {options["days"]} days.'
                )
            )
        
        # Show statistics
        with_session = Prediction.objects.filter(
            session_key__isnull=False,
            is_archived=False
        ).count()
        
        with_user = Prediction.objects.filter(
            user__isnull=False,
            is_archived=False
        ).count()
        
        self.stdout.write(f'\nStatistics:')
        self.stdout.write(f'  - Predictions with session_key: {with_session}')
        self.stdout.write(f'  - Predictions with user: {with_user}')
        self.stdout.write(f'  - Predictions without both: {total_count}')

