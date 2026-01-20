from django.core.management.base import BaseCommand
from predictor.models import League, Team
from django.core.cache import cache

class Command(BaseCommand):
    help = 'Populates the database with exact European and Other leagues/teams'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting data population...')
        
        # 1. European Leagues Data
        euro_data = {
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

        # 2. Others Leagues Data
        others_data = {
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

        # Process European
        self.populate_category("European Leagues", euro_data)
        # Process Others
        self.populate_category("Others", others_data)

        # Clear Cache
        cache.delete('leagues_by_category_db')
        self.stdout.write(self.style.SUCCESS('Successfully populated all leagues and teams!'))

    def populate_category(self, category, data_dict):
        for league_name, teams in data_dict.items():
            league, created = League.objects.get_or_create(
                name=league_name,
                defaults={'category': category}
            )
            
            if created:
                self.stdout.write(f"  Created: {league_name}")
            else:
                if league.category != category:
                    league.category = category
                    league.save()
                    self.stdout.write(f"  Updated category for: {league_name}")

            # Optimize finding existing teams to minimize DB hits? 
            # For simplicity in this seed script, just iterate.
            for team_name in teams:
                team, t_created = Team.objects.get_or_create(
                    name=team_name,
                    defaults={'league': league}
                )
                
                if not t_created and team.league != league:
                    self.stdout.write(f"    Moving {team.name} to {league.name}")
                    team.league = league
                    team.save()
