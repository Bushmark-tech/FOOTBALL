import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.models import League, Team

def populate_data_v2(all_leagues):
    for league_name, teams in all_leagues.items():
        if league_name == "English Premier League":
            cat = "European Leagues"
        else:
            cat = "Others"

        league, created = League.objects.get_or_create(
            name=league_name,
            defaults={'category': cat}
        )
        if created:
            print(f"Created League: {league.name}")
        else:
            print(f"Found League: {league.name}")
            if league.category != cat:
                league.category = cat
                league.save()
        
        print(f"Populating {len(teams)} teams for {league.name}...")
        for team_name in teams:
            # Handle unique name constraint
            existing_team = Team.objects.filter(name=team_name).first()
            if existing_team:
                if existing_team.league != league:
                    print(f"Moving {team_name} from {existing_team.league.name} to {league.name}")
                    existing_team.league = league
                    existing_team.save()
            else:
                Team.objects.create(name=team_name, league=league)

    # Clear Cache
    from django.core.cache import cache
    cache.delete('leagues_by_category_db')
    print("Cache cleared.")

if __name__ == "__main__":
    # Combined dictionary for cleaner iteration
    all_data = {
        "English Premier League": [
            "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton",
            "Burnley", "Chelsea", "Crystal Palace", "Everton", "Fulham",
            "Liverpool", "Luton Town", "Manchester City", "Manchester United",
            "Newcastle United", "Nottingham Forest", "Sheffield United",
            "Tottenham Hotspur", "West Ham United", "Wolverhampton Wanderers"
        ],
        "Switzerland": [
            "Sion", "St. Gallen", "Thun", "Zurich", "Young Boys", "Servette",
            "Basel", "Luzern", "Lugano", "Lausanne", "Grasshoppers", "Winterthur"
        ],
        "Denmark": [
            "Midtjylland", "Odense", "Sonderjyske", "Brondby", "FC Copenhagen",
            "Silkeborg", "Randers FC", "Aarhus", "Nordsjaelland", "Vejle",
            "Viborg", "Fredericia"
        ],
        "Austria": [
            "SK Rapid", "Tirol", "LASK", "Sturm Graz", "Austria Vienna",
            "Altach", "Hartberg", "Salzburg", "Wolfsberger AC", "Ried",
            "BW Linz", "Grazer AK"
        ],
        "Mexico": [
            "Atlas", "Atl. San Luis", "Puebla", "Pachuca", "Necaxa", "Tigres UANL",
            "Toluca", "Club America", "Santos Laguna", "Club Tijuana", "UNAM Pumas",
            "Club Leon", "Cruz Azul", "Guadalajara Chivas", "Queretaro", "Monterrey",
            "Juarez", "Mazatlan FC"
        ],
        "Russia": [
            "FK Rostov", "Spartak Moscow", "Zenit", "Krylya Sovetov", "Akhmat Grozny",
            "Lokomotiv Moscow", "CSKA Moscow", "Dynamo Moscow", "Sochi", "Krasnodar",
            "Orenburg", "Rubin Kazan", "Pari NN", "Baltika", "Akron Togliatti",
            "Dynamo Makhachkala"
        ],
        "Romania": [
            "CFR Cluj", "FCSB", "FC Hermannstadt", "FC Botosani", "Din. Bucuresti",
            "FC Arges", "UTA Arad", "Univ. Craiova", "FC Rapid Bucuresti",
            "Farul Constanta", "U. Cluj", "Petrolul", "Otelul", "Csikszereda M. Ciuc",
            "Unirea Slobozia", "Metaloglobus Bucharest"
        ]
    }
    
    # Run population
    populate_data_v2(all_data)
