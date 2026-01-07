# Auto-cleanup duplicate predictions using Django signals

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from predictor.models import Prediction
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Prediction)
def cleanup_duplicate_predictions(sender, instance, created, **kwargs):
    """
    Automatically delete duplicate predictions when a new one is saved.
    A duplicate is defined as: same user/session, same teams, within 30 seconds.
    """
    if not created:
        return  # Only check for duplicates on new predictions
    
    try:
        # Define time window for duplicates (30 seconds)
        time_window_start = instance.prediction_date - timedelta(seconds=30)
        time_window_end = instance.prediction_date + timedelta(seconds=30)
        
        # Find duplicates
        if instance.user:
            duplicates = Prediction.objects.filter(
                user=instance.user,
                home_team=instance.home_team,
                away_team=instance.away_team,
                prediction_date__gte=time_window_start,
                prediction_date__lte=time_window_end
            ).exclude(id=instance.id).order_by('id')
        elif instance.session_key:
            duplicates = Prediction.objects.filter(
                session_key=instance.session_key,
                home_team=instance.home_team,
                away_team=instance.away_team,
                prediction_date__gte=time_window_start,
                prediction_date__lte=time_window_end
            ).exclude(id=instance.id).order_by('id')
        else:
            return  # No user or session, can't determine duplicates
        
        # Delete duplicates (keep the current instance)
        if duplicates.exists():
            count = duplicates.count()
            duplicates.delete()
            logger.info(f"Auto-deleted {count} duplicate prediction(s) for {instance.home_team} vs {instance.away_team} (kept ID: {instance.id})")
    
    except Exception as e:
        logger.error(f"Error in duplicate cleanup signal: {e}")
