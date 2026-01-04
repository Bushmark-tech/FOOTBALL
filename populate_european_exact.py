import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.models import League, Team
from django.core.cache import cache

def populate_european_exact():
    data = {
        "🏴 EPL (Premier League)": [
            "Nott'm Forest", "Brentford", "Liverpool", "Leeds", "Fulham", 
            "Tottenham", "Burnley", "Crystal Palace", "West Ham", "Bournemouth", 
            "Newcastle", "Man United", "Arsenal", "Brighton", "Everton", 
            "Aston Villa", "Man City", "Chelsea", "Wolves", "Sunderland"
        ],
        "🇬🇧 Championship": [
            "Millwall", "Swansea", "Stoke", "Blackburn", "Bristol City", 
            "Birmingham", "Charlton", "Derby", "Hull", "Preston", "QPR", 
            "Sheffield Weds", "West Brom", "Middlesbrough", "Watford", 
            "Leicester", "Norwich", "Southampton", "Sheffield United", 
            "Coventry", "Ipswich", "Oxford", "Portsmouth", "Wrexham"
        ],
        "🏴 Scotland": [
            "Celtic", "Hibernian", "Livingston", "Aberdeen", "Kilmarnock", 
            "Hearts", "Motherwell", "Rangers", "St Mirren", "Dundee United", 
            "Dundee", "Falkirk"
        ],
        "🇩🇪 Bundesliga": [
            "Stuttgart", "Hamburg", "St Pauli", "Heidenheim", "Bayern Munich", 
            "M'gladbach", "Wolfsburg", "Werder Bremen", "Leverkusen", "Freiburg", 
            "Dortmund", "Ein Frankfurt", "Union Berlin", "FC Koln", "Hoffenheim", 
            "Mainz", "Augsburg", "RB Leipzig"
        ],
        "🇩🇪 Bundesliga 2": [
            "Dresden", "Holstein Kiel", "Greuther Furth", "Bielefeld", "Bochum", 
            "Hannover", "Karlsruhe", "Darmstadt", "Nurnberg", "Schalke 04", 
            "Paderborn", "Fortuna Dusseldorf", "Hertha", "Braunschweig", 
            "Kaiserslautern", "Magdeburg", "Elversberg"
        ],
        "🇮🇹 Serie A": [
            "Pisa", "Fiorentina", "Parma", "Roma", "Cagliari", "Udinese", 
            "Torino", "Verona", "Inter", "Bologna", "Milan", "Cremonese", 
            "Juventus", "Atalanta", "Genoa", "Lecce", "Sassuolo", "Lazio", 
            "Napoli", "Como"
        ],
        "🇮🇹 Serie B": [
            "Virtus Entella", "Venezia", "Sampdoria", "Empoli", "Spezia", 
            "Frosinone", "Pescara", "Juve Stabia", "Monza", "Reggiana", 
            "Palermo", "Modena", "Bari", "Sudtirol", "Catanzaro", "Cesena", 
            "Mantova", "Carrarese", "Avellino", "Padova"
        ],
        "🇪🇸 LaLiga": [
            "Ath Bilbao", "Elche", "Vallecano", "Celta", "Valencia", "Mallorca", 
            "Villarreal", "Espanol", "Girona", "Ath Madrid", "Betis", "Alaves", 
            "Levante", "Osasuna", "Getafe", "Real Madrid", "Oviedo", "Barcelona", 
            "Sevilla", "Sociedad"
        ],
        "🇪🇸 LaLiga 2": [
            "Santander", "Zaragoza", "Almeria", "Leganes", "Las Palmas", "Cadiz", 
            "La Coruna", "Granada", "Albacete", "Malaga", "Mirandes", "Huesca", 
            "Sp Gijon", "Valladolid", "Eibar", "Castellon", "Sociedad B", 
            "Burgos", "Andorra", "Cordoba", "Ceuta", "Cultural Leonesa"
        ],
        "🇫🇷 Ligue 1": [
            "Lorient", "Le Havre", "Paris FC", "Auxerre", "Lens", "Monaco", 
            "Marseille", "Angers", "Brest", "Nice", "Lille", "Strasbourg", 
            "Paris SG", "Lyon", "Nantes", "Toulouse", "Metz", "Rennes"
        ],
        "🇫🇷 Ligue 2": [
            "Clermont", "Guingamp", "Nancy", "Rodez", "Le Mans", "Troyes", 
            "Grenoble", "Montpellier", "Amiens", "Reims", "St Etienne", 
            "Pau FC", "Dunkerque", "Bastia", "Annecy", "Laval", "Red Star", 
            "Boulogne"
        ],
        "🇳🇱 Eredivisie": [
            "Zwolle", "Twente", "AZ Alkmaar", "Feyenoord", "Heracles", 
            "Sparta Rotterdam", "Groningen", "Ajax", "For Sittard", "Utrecht", 
            "Heerenveen", "PSV Eindhoven", "Go Ahead Eagles", "Nijmegen", 
            "Excelsior", "Volendam", "NAC Breda", "Telstar"
        ],
        "🇧🇪 Belgium": [
            "Genk", "Cercle Brugge", "St Truiden", "Waregem", "Anderlecht", 
            "Charleroi", "Club Brugge", "Mechelen", "Standard", "Gent", 
            "Antwerp", "Oud-Heverlee Leuven", "St. Gilloise", "Westerlo", 
            "Dender", "RAAL La Louviere"
        ],
        "🇵🇹 Portugal": [
            "Benfica", "Gil Vicente", "Santa Clara", "Sp Braga", "Famalicao", 
            "Porto", "Moreirense", "Sp Lisbon", "Guimaraes", "Tondela", 
            "Rio Ave", "Nacional", "Arouca", "Estoril", "Casa Pia", "Estrela", 
            "AVS", "Alverca"
        ],
        "🇹🇷 Turkey": [
            "Genclerbirligi", "Kayserispor", "Konyaspor", "Goztep", "Kasimpasa", 
            "Fenerbahce", "Besiktas", "Alanyaspor", "Buyuksehyr", "Galatasaray", 
            "Rizespor", "Trabzonspor", "Antalyaspor", "Gaziantep", "Karagumruk", 
            "Samsunspor", "Eyupspor", "Kocaelispor"
        ],
        "🇬🇷 Greece": [
            "Aris", "Olympiakos", "AEK", "Atromitos", "PAOK", "Panetolikos", 
            "Panathinaikos", "Volos NFC", "Asteras Tripolis", "Larisa", 
            "OFI Crete", "Levadeiakos", "Kifisia", "Panserraikos"
        ]
    }

    print("Populating European Leagues with EXACT user data...")

    # Identify leagues to remove (old names) to avoid duplicates like "English Premier League" vs "EPL (Premier League)"
    # We will rename if possible, or create new and delete old.
    
    # 1. Map old names to new names roughly to try and rename inplace if possible to preserve IDs? 
    # Not strictly necessary if we just clear and repopulate, but cleaner.
    # Let's just create/get the NEW names.
    
    for league_name, teams in data.items():
        league, created = League.objects.get_or_create(
            name=league_name,
            defaults={'category': "European Leagues"}
        )
        if created:
            print(f"Created League: {league.name}")
        else:
            print(f"Update League: {league.name}")
            if league.category != "European Leagues":
                league.category = "European Leagues"
                league.save()

        # Update Teams
        # We want the league to contain ONLY these teams.
        # But we must be careful not to delete teams if they are just moved?
        # Actually, user wants these exact teams.
        
        current_teams = set(league.teams.values_list('name', flat=True))
        target_teams = set(teams)
        
        # Add missing teams
        for team_name in target_teams:
            # Check if team exists anywhere
            t = Team.objects.filter(name=team_name).first()
            if t:
                if t.league != league:
                    print(f"  Moving {t.name} to {league.name} (from {t.league.name})")
                    t.league = league
                    t.save()
            else:
                print(f"  Creating {team_name} in {league.name}")
                Team.objects.create(name=team_name, league=league)
        
        # Remove extra teams? user said "this teamatoppolaate" implying this is the list.
        # Let's NOT delete teams immediately unless we are sure, to avoid data loss.
        # But for the dropdown to be "exact", we should probably ensure no others are linked.
        # However, safe approach: just ensure these exist.
        
    
    # Cleaning up old similar names to avoid confusion in dropdown
    # e.g. "English Premier League" -> delete if now we have "🏴 EPL (Premier League)"
    cleanups = [
        "English Premier League", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League", 
        "English Championship", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Championship",
        "Scotland Premiership", "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Premiership",
        "Germany Bundesliga", "🇩🇪 Bundesliga 1",
        "Spain La Liga", "🇪🇸 La Liga",
        "France Ligue 1", "🇫🇷 Ligue 1"
    ]
    
    for old_name in cleanups:
        # Only delete if it's NOT one of the new keys
        if old_name not in data:
            old_l = League.objects.filter(name=old_name).first()
            if old_l:
                # Check if it has teams that we didn't move? 
                # If we moved all teams, it should be empty or close to it.
                count = old_l.teams.count()
                if count < 5: # Threshold
                    print(f"Removing old league: {old_name} ({count} teams)")
                    old_l.delete()
                else:
                    print(f"WARNING: Old league {old_name} still has {count} teams. Renaming to [OLD] {old_name}")
                    old_l.name = f"[OLD] {old_name}"
                    old_l.save()

    cache.delete('leagues_by_category_db')
    print("Done.")

if __name__ == "__main__":
    populate_european_exact()
