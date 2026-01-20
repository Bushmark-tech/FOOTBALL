import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.models import League, Team
from django.core.cache import cache

def populate_others_exact():
    # User provided list for "Others" category
    # Adding 🇨🇭 flag to Switzerland for consistency with other inputs, 
    # even though prompt text was slightly ambiguous there (likely copy-paste truncation).
    data = {
        "🇨🇭 Switzerland": [
            "Sion", "St. Gallen", "Thun", "Zurich", "Young Boys", "Servette",
            "Basel", "Luzern", "Lugano", "Lausanne", "Grasshoppers", "Winterthur"
        ],
        "🇩🇰 Denmark": [
            "Midtjylland", "Odense", "Sonderjyske", "Brondby", "FC Copenhagen",
            "Silkeborg", "Randers FC", "Aarhus", "Nordsjaelland", "Vejle",
            "Viborg", "Fredericia"
        ],
        "🇦🇹 Austria": [
            "SK Rapid", "Tirol", "LASK", "Sturm Graz", "Austria Vienna",
            "Altach", "Hartberg", "Salzburg", "Wolfsberger AC", "Ried",
            "BW Linz", "Grazer AK"
        ],
        "🇲🇽 Mexico": [
            "Atlas", "Atl. San Luis", "Puebla", "Pachuca", "Necaxa", "Tigres UANL",
            "Toluca", "Club America", "Santos Laguna", "Club Tijuana", "UNAM Pumas",
            "Club Leon", "Cruz Azul", "Guadalajara Chivas", "Queretaro", "Monterrey",
            "Juarez", "Mazatlan FC"
        ],
        "🇷🇺 Russia": [
            "FK Rostov", "Spartak Moscow", "Zenit", "Krylya Sovetov", "Akhmat Grozny",
            "Lokomotiv Moscow", "CSKA Moscow", "Dynamo Moscow", "Sochi", "Krasnodar",
            "Orenburg", "Rubin Kazan", "Pari NN", "Baltika", "Akron Togliatti",
            "Dynamo Makhachkala"
        ],
        "🇷🇴 Romania": [
            "CFR Cluj", "FCSB", "FC Hermannstadt", "FC Botosani", "Din. Bucuresti",
            "FC Arges", "UTA Arad", "Univ. Craiova", "FC Rapid Bucuresti",
            "Farul Constanta", "U. Cluj", "Petrolul", "Otelul", "Csikszereda M. Ciuc",
            "Unirea Slobozia", "Metaloglobus Bucharest"
        ]
    }

    print("Populating 'Others' Leagues with EXACT user data...")

    for league_name, teams in data.items():
        # Get or create the league
        league, created = League.objects.get_or_create(
            name=league_name,
            defaults={'category': "Others"}
        )
        if created:
            print(f"Created League: {league.name}")
        else:
            print(f"Found/Updated League: {league.name}")
            # Ensure it is in "Others"
            if league.category != "Others":
                league.category = "Others"
                league.save()

        # Update Teams
        print(f"  Populating {len(teams)} teams for {league.name}...")
        
        for team_name in teams:
            # Check if team exists anywhere
            t = Team.objects.filter(name=team_name).first()
            if t:
                if t.league != league:
                    print(f"   Moving {t.name} to {league_name} (was in {t.league.name})")
                    t.league = league
                    t.save()
            else:
                Team.objects.create(name=team_name, league=league)

    # Cleanup: Remove old leagues that don't match the new flagged names if they exist
    # e.g. "Switzerland" (no flag) if we now use "🇨🇭 Switzerland"
    # We only delete if they are empty or if we are sure we migrated everyone.
    # Since we moved teams by name above, if the old league had these teams, they are now empty.
    
    old_names = [
        "Switzerland", "Denmark", "Austria", "Mexico", "Russia", "Romania",
        "Swiss Super League", "Danish Superliga", "Austrian Bundesliga"
    ]
    
    for old in old_names:
        # Don't delete if it matches a new name key (check just in case)
        if old not in data:
            old_l = League.objects.filter(name=old).first()
            if old_l:
                count = old_l.teams.count()
                if count == 0:
                    print(f"Removing empty old league: {old}")
                    old_l.delete()
                else:
                    print(f"Old league {old} still contains {count} teams - skipping delete.")

    # Clear cache
    cache.delete('leagues_by_category_db')
    print("FINISHED: 'Others' Data Populated & Cache Cleared.")

if __name__ == "__main__":
    populate_others_exact()
