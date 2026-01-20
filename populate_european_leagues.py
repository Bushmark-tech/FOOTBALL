import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.models import League, Team

def populate_european_data():
    european_leagues = {
        "English Premier League": [
            "Nott'm Forest", "Brentford", "Liverpool", "Leeds", "Fulham", 
            "Tottenham", "Burnley", "Crystal Palace", "West Ham", "Bournemouth", 
            "Newcastle", "Man United", "Arsenal", "Brighton", "Everton", 
            "Aston Villa", "Man City", "Chelsea", "Wolves", "Sunderland"
        ],
        "English Championship": [
            "Millwall", "Swansea", "Stoke", "Blackburn", "Bristol City", 
            "Birmingham", "Charlton", "Derby", "Hull", "Preston", "QPR", 
            "Sheffield Weds", "West Brom", "Middlesbrough", "Watford", 
            "Leicester", "Norwich", "Southampton", "Sheffield United", 
            "Coventry", "Ipswich", "Oxford", "Portsmouth", "Wrexham"
        ],
        "Scotland Premiership": [
            "Celtic", "Hibernian", "Livingston", "Aberdeen", "Kilmarnock", 
            "Hearts", "Motherwell", "Rangers", "St Mirren", "Dundee United", 
            "Dundee", "Falkirk"
        ],
        "Germany Bundesliga": [
            "Stuttgart", "Hamburg", "St Pauli", "Heidenheim", "Bayern Munich", 
            "M'gladbach", "Wolfsburg", "Werder Bremen", "Leverkusen", "Freiburg", 
            "Dortmund", "Ein Frankfurt", "Union Berlin", "FC Koln", "Hoffenheim", 
            "Mainz", "Augsburg", "RB Leipzig"
        ],
        "Germany 2. Bundesliga": [
            "Dresden", "Holstein Kiel", "Greuther Furth", "Bielefeld", "Bochum", 
            "Hannover", "Karlsruhe", "Darmstadt", "Nurnberg", "Schalke 04", 
            "Paderborn", "Fortuna Dusseldorf", "Hertha", "Braunschweig", 
            "Kaiserslautern", "Magdeburg", "Elversberg"
        ],
        "Italy Serie A": [
            "Pisa", "Fiorentina", "Parma", "Roma", "Cagliari", "Udinese", 
            "Torino", "Verona", "Inter", "Bologna", "Milan", "Cremonese", 
            "Juventus", "Atalanta", "Genoa", "Lecce", "Sassuolo", "Lazio", 
            "Napoli", "Como"
        ],
        "Italy Serie B": [
            "Virtus Entella", "Venezia", "Sampdoria", "Empoli", "Spezia", 
            "Frosinone", "Pescara", "Juve Stabia", "Monza", "Reggiana", 
            "Palermo", "Modena", "Bari", "Sudtirol", "Catanzaro", "Cesena", 
            "Mantova", "Carrarese", "Avellino", "Padova"
        ],
        "Spain La Liga": [
            "Ath Bilbao", "Elche", "Vallecano", "Celta", "Valencia", "Mallorca", 
            "Villarreal", "Espanol", "Girona", "Ath Madrid", "Betis", "Alaves", 
            "Levante", "Osasuna", "Getafe", "Real Madrid", "Oviedo", "Barcelona", 
            "Sevilla", "Sociedad"
        ],
        "Spain La Liga 2": [
            "Santander", "Zaragoza", "Almeria", "Leganes", "Las Palmas", "Cadiz", 
            "La Coruna", "Granada", "Albacete", "Malaga", "Mirandes", "Huesca", 
            "Sp Gijon", "Valladolid", "Eibar", "Castellon", "Sociedad B", 
            "Burgos", "Andorra", "Cordoba", "Ceuta", "Cultural Leonesa"
        ],
        "France Ligue 1": [
            "Lorient", "Le Havre", "Paris FC", "Auxerre", "Lens", "Monaco", 
            "Marseille", "Angers", "Brest", "Nice", "Lille", "Strasbourg", 
            "Paris SG", "Lyon", "Nantes", "Toulouse", "Metz", "Rennes"
        ],
        "France Ligue 2": [
            "Clermont", "Guingamp", "Nancy", "Rodez", "Le Mans", "Troyes", 
            "Grenoble", "Montpellier", "Amiens", "Reims", "St Etienne", 
            "Pau FC", "Dunkerque", "Bastia", "Annecy", "Laval", "Red Star", 
            "Boulogne"
        ],
        "Netherlands Eredivisie": [
            "Zwolle", "Twente", "AZ Alkmaar", "Feyenoord", "Heracles", 
            "Sparta Rotterdam", "Groningen", "Ajax", "For Sittard", "Utrecht", 
            "Heerenveen", "PSV Eindhoven", "Go Ahead Eagles", "Nijmegen", 
            "Excelsior", "Volendam", "NAC Breda", "Telstar"
        ],
        "Belgium Pro League": [
            "Genk", "Cercle Brugge", "St Truiden", "Waregem", "Anderlecht", 
            "Charleroi", "Club Brugge", "Mechelen", "Standard", "Gent", 
            "Antwerp", "Oud-Heverlee Leuven", "St. Gilloise", "Westerlo", 
            "Dender", "RAAL La Louviere"
        ],
        "Portugal Primeira Liga": [
            "Benfica", "Gil Vicente", "Santa Clara", "Sp Braga", "Famalicao", 
            "Porto", "Moreirense", "Sp Lisbon", "Guimaraes", "Tondela", 
            "Rio Ave", "Nacional", "Arouca", "Estoril", "Casa Pia", "Estrela", 
            "AVS", "Alverca"
        ],
        "Turkey Super Lig": [
            "Genclerbirligi", "Kayserispor", "Konyaspor", "Goztep", "Kasimpasa", 
            "Fenerbahce", "Besiktas", "Alanyaspor", "Buyuksehyr", "Galatasaray", 
            "Rizespor", "Trabzonspor", "Antalyaspor", "Gaziantep", "Karagumruk", 
            "Samsunspor", "Eyupspor", "Kocaelispor"
        ],
        "Greece Super League": [
            "Aris", "Olympiakos", "AEK", "Atromitos", "PAOK", "Panetolikos", 
            "Panathinaikos", "Volos NFC", "Asteras Tripolis", "Larisa", 
            "OFI Crete", "Levadeiakos", "Kifisia", "Panserraikos"
        ]
    }

    print("Starting European Leagues Population...")
    
    for league_name, teams in european_leagues.items():
        league, created = League.objects.get_or_create(
            name=league_name,
            defaults={'category': "European Leagues"}
        )
        
        if created:
            print(f"Created League: {league.name}")
        else:
            print(f"Update League: {league.name}")
            # Ensure proper category
            if league.category != "European Leagues":
                league.category = "European Leagues"
                league.save()

        print(f"  Adding {len(teams)} teams...")
        
        for team_name in teams:
            # Check for existing team to handle unique constraints/transfers
            existing_team = Team.objects.filter(name=team_name).first()
            
            if existing_team:
                if existing_team.league != league:
                    print(f"   Moving {team_name} from {existing_team.league.name} to {league.name}")
                    existing_team.league = league
                    existing_team.save()
            else:
                Team.objects.create(name=team_name, league=league)

    # Clear cache
    from django.core.cache import cache
    cache.delete('leagues_by_category_db')
    print("FINISHED: European Data Populated & Cache Cleared and Updated.")

if __name__ == "__main__":
    populate_european_data()
