
import os
import django
import sys
import codecs

# Setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.models import Prediction, BillingUsage
from predictor.views import get_league_for_team
from django.db.models import Q

def fix_leagues_user():
    # Fix encoding
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    
    print("Checking League Logic:")
    teams_to_check = ['Man United', 'Young Boys', 'Grasshoppers', 'Bournemouth', 'Arsenal']
    for t in teams_to_check:
        print(f"  Team: {t} -> League: '{get_league_for_team(t)}'")

    print("\nFixing Prediction Leagues...")
    # Get all predictions
    preds = Prediction.objects.all()
    count = 0
    updated = 0
    
    for p in preds:
        original_league = p.league
        
        # Determine correct league
        new_league = get_league_for_team(p.home_team)
        if not new_league:
            new_league = get_league_for_team(p.away_team)
            
        if new_league and new_league != original_league:
            print(f"  Updating ID {p.id} ({p.home_team} vs {p.away_team}): '{original_league}' -> '{new_league}'")
            p.league = new_league
            p.save()
            updated += 1
        count += 1
        
    print(f"\nProcessed {count} predictions, updated {updated}.")
    
    # Recalculate stats
    print("\nRecalculating Billing Stats...")
    for b in BillingUsage.objects.all():
        b.update_statistics()
        print(f"  User {b.user} -> Leagues: {b.unique_leagues_count}")

if __name__ == '__main__':
    fix_leagues_user()
