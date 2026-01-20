import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.models import League
from django.core.cache import cache

def update_league_names():
    # Mapping of Current Name -> New Name with Flag
    name_mapping = {
        # European Leagues
        "English Premier League": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League",
        "English Championship": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Championship",
        "Scotland Premiership": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Premiership",
        "Germany Bundesliga": "🇩🇪 Bundesliga 1",
        "Germany 2. Bundesliga": "🇩🇪 Bundesliga 2",
        "Italy Serie A": "🇮🇹 Serie A",
        "Italy Serie B": "🇮🇹 Serie B",
        "Spain La Liga": "🇪🇸 La Liga",
        "Spain La Liga 2": "🇪🇸 La Liga 2",
        "France Ligue 1": "🇫🇷 Ligue 1",
        "France Ligue 2": "🇫🇷 Ligue 2",
        "Netherlands Eredivisie": "🇳🇱 Eredivisie",
        "Belgium Pro League": "🇧🇪 Pro League",
        "Portugal Primeira Liga": "🇵🇹 Primeira Liga",
        "Turkey Super Lig": "🇹🇷 Super Lig",
        "Greece Super League": "🇬🇷 Super League",
        
        # Others
        "Switzerland": "🇨🇭 Switzerland",
        "Denmark": "🇩🇰 Denmark",
        "Austria": "🇦🇹 Austria",
        "Mexico": "🇲🇽 Mexico",
        "Russia": "🇷🇺 Russia",
        "Romania": "🇷🇴 Romania"
    }

    print("Updating League Names to include Flags...")
    
    for old_name, new_name in name_mapping.items():
        try:
            league = League.objects.filter(name=old_name).first()
            if league:
                # Check if new name already exists (idempotency)
                if League.objects.filter(name=new_name).exists():
                    print(f"Skipping {old_name}: {new_name} already exists.")
                    # If the old one still exists separately, we might want to merge, 
                    # but for now let's assume we just rename.
                    # Actually, if we rename and it conflicts, we have a problem.
                    # So we only rename if new_name doesn't exist.
                else:
                    league.name = new_name
                    league.save()
                    print(f"Updated: {old_name} -> {new_name}")
            else:
                # Maybe it's already updated?
                if League.objects.filter(name=new_name).exists():
                    print(f"Already updated: {new_name}")
                else:
                    print(f"Not Found: {old_name}")
        except Exception as e:
            print(f"Error updating {old_name}: {e}")

    # Clear cache to ensure new names appear immediately
    cache.delete('leagues_by_category_db')
    print("Cache cleared. Update Complete.")

if __name__ == "__main__":
    update_league_names()
