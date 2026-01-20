import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.models import League

def cleanup_empty_leagues():
    print("Checking for empty or duplicate leagues...")
    all_leagues = League.objects.all()
    count = 0
    for league in all_leagues:
        team_count = league.teams.count()
        # Criteria for removal:
        # 1. No teams
        # 2. Name seems generic (like "Europe League" instead of specific) AND has no teams
        
        if team_count == 0:
            print(f"Deleting empty league: {league.name} (Category: {league.category})")
            league.delete()
            count += 1
        else:
            print(f"Keeping: {league.name} ({team_count} teams)")
            
    print(f"Cleanup Complete. Deleted {count} empty leagues.")

    # Clear cache again
    from django.core.cache import cache
    cache.delete('leagues_by_category_db')

if __name__ == "__main__":
    cleanup_empty_leagues()
