#!/usr/bin/env python
"""Script to clear caches and clean up old predictions."""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from django.core.cache import cache
from predictor.models import Prediction
from predictor.analytics import clear_data_cache, _data_cache

def clear_all_caches():
    """Clear all caches."""
    print("\n" + "="*60)
    print("Clearing All Caches")
    print("="*60)
    
    # Clear Django cache (Redis/Database)
    try:
        cache.clear()
        print("✓ Cleared Django cache (Redis/Database)")
    except Exception as e:
        print(f"⚠ Could not clear Django cache: {e}")
    
    # Clear in-memory data cache
    try:
        _data_cache.clear()
        clear_data_cache()
        print("✓ Cleared in-memory data cache")
    except Exception as e:
        print(f"⚠ Could not clear data cache: {e}")
    
    print("\nAll caches cleared!")

def cleanup_duplicate_predictions():
    """Remove duplicate predictions for the same match."""
    print("\n" + "="*60)
    print("Cleaning Up Duplicate Predictions")
    print("="*60)
    
    # Find predictions for Chelsea vs Crystal Palace
    chelsea_predictions = Prediction.objects.filter(
        home_team__iexact='Chelsea',
        away_team__iexact='Crystal Palace'
    ).order_by('-prediction_date')
    
    count = chelsea_predictions.count()
    print(f"Found {count} predictions for Chelsea vs Crystal Palace")
    
    if count > 0:
        # Keep only the most recent one
        most_recent = chelsea_predictions.first()
        old_predictions = chelsea_predictions.exclude(id=most_recent.id)
        old_count = old_predictions.count()
        
        if old_count > 0:
            print(f"Keeping most recent prediction (ID: {most_recent.id}, Date: {most_recent.prediction_date})")
            print(f"Deleting {old_count} older predictions...")
            old_predictions.delete()
            print(f"✓ Deleted {old_count} old predictions")
        else:
            print("✓ No duplicates found")
    
    print("\nCleanup complete!")

def show_current_predictions():
    """Show current predictions for Chelsea vs Crystal Palace."""
    print("\n" + "="*60)
    print("Current Predictions for Chelsea vs Crystal Palace")
    print("="*60)
    
    predictions = Prediction.objects.filter(
        home_team__iexact='Chelsea',
        away_team__iexact='Crystal Palace'
    ).order_by('-prediction_date')
    
    if predictions.exists():
        for pred in predictions:
            print(f"\nID: {pred.id}")
            print(f"Date: {pred.prediction_date}")
            print(f"Probabilities: Home={pred.prob_home*100:.1f}%, Draw={pred.prob_draw*100:.1f}%, Away={pred.prob_away*100:.1f}%")
            print(f"Outcome: {pred.outcome}")
    else:
        print("No predictions found")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Cache and Database Cleanup Script")
    print("="*60)
    
    # Show current state
    show_current_predictions()
    
    # Clear caches
    clear_all_caches()
    
    # Cleanup duplicates
    cleanup_duplicate_predictions()
    
    # Show final state
    show_current_predictions()
    
    print("\n" + "="*60)
    print("✓ All done! Caches cleared and database cleaned.")
    print("="*60 + "\n")

