from django.core.management.base import BaseCommand
from predictor.models import League, Team

# Copy of LEAGUES_BY_CATEGORY from views.py
LEAGUES_BY_CATEGORY = {
    'European Leagues': {
        "Premier League": sorted(['Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton', 'Chelsea', 'Crystal Palace',
                                  'Everton', 'Fulham', 'Ipswich', 'Leicester', 'Liverpool', 'Man City', 'Man United', 'Newcastle',
                                  "Nott'm Forest", 'Southampton', 'Tottenham', 'West Ham', 'Wolves']),
        "English Championship": sorted(['Blackburn', 'Derby', 'Preston', 'Sheffield United', 'Cardiff', 'Sunderland','Hull',
                                         'Bristol City', 'Leeds', 'Portsmouth', 'Middlesbrough', 'Swansea','Millwall', 'Watford',
                                         'Oxford', 'Norwich', 'QPR', 'West Brom', 'Stoke','Coventry', 'Sheffield Weds', 'Plymouth',
                                         'Luton', 'Burnley']),
        "Serie A": sorted(['Atalanta', 'Bologna', 'Cagliari', 'Como', 'Empoli', 'Fiorentina', 'Genoa', 'Inter',
                           'Juventus', 'Lazio', 'Lecce', 'Milan', 'Monza', 'Napoli', 'Parma', 'Roma', 'Torino',
                           'Udinese', 'Venezia', 'Verona']),
        "Serie B": sorted(['Bari', 'Brescia', 'Carrarese', 'Catanzaro', 'Cesena', 'Cittadella', 'Cosenza', 'Cremonese',
                           'Frosinone', 'Juve Stabia', 'Mantova', 'Modena', 'Palermo', 'Pisa', 'Reggiana', 'Salernitana',
                           'Sampdoria', 'Sassuolo', 'Spezia', 'Sudtirol']),
        "Ligue1": sorted(['Angers', 'Auxerre', 'Brest', 'Lens', 'Le Havre', 'Lille', 'Lyon', 'Marseille',
                          'Monaco', 'Montpellier', 'Nantes', 'Nice', 'Paris SG', 'Reims', 'Rennes',
                          'St Etienne', 'Strasbourg', 'Toulouse']),
        "Ligue2": sorted(['Ajaccio', 'Rodez', 'Amiens', 'Red Star', 'Clermont', 'Pau FC', 'Dunkerque',
                          'Annecy', 'Grenoble', 'Laval', 'Guingamp', 'Troyes', 'Caen', 'Paris FC',
                          'Martigues', 'Lorient', 'Metz', 'Bastia']),
        "La Liga": sorted(['Alaves', 'Ath Bilbao', 'Ath Madrid', 'Barcelona', 'Betis', 'Celta', 'Espanol', 'Getafe',
                           'Girona', 'Las Palmas', 'Leganes', 'Mallorca', 'Osasuna', 'Real Madrid', 'Sevilla', 'Sociedad',
                           'Valencia', 'Valladolid', 'Vallecano', 'Villarreal']),
        "La Liga2": sorted(['Albacete', 'Almeria', 'Burgos', 'Cadiz', 'Cartagena', 'Castellon', 'Cordoba', 'Eibar',
                            'Eldense', 'Elche', 'Ferrol', 'Granada', 'Huesca', 'La Coruna', 'Levante', 'Malaga',
                            'Mirandes', 'Oviedo', 'Santander', 'Sp Gijon', 'Tenerife', 'Zaragoza']),
        "Eredivisie": sorted(['Ajax', 'Almere City', 'AZ Alkmaar', 'Feyenoord', 'For Sittard', 'Go Ahead Eagles', 'Groningen',
                              'Heerenveen', 'Heracles', 'NAC Breda', 'Nijmegen', 'PSV Eindhoven', 'Sparta Rotterdam',
                              'Twente', 'Utrecht', 'Waalwijk', 'Willem II', 'Zwolle']),
        "Bundesliga": sorted(['Augsburg', 'Bayern Munich', 'Bochum', 'Dortmund', 'Ein Frankfurt', 'Freiburg',
                              'Heidenheim', 'Hoffenheim', 'Holstein Kiel', 'Leverkusen', 'M\'gladbach', 'Mainz', 'RB Leipzig',
                              'St Pauli', 'Stuttgart', 'Union Berlin', 'Werder Bremen', 'Wolfsburg']),
        "Bundesliga2": sorted(['Hamburg', 'Schalke 04', 'Hannover', 'Elversberg', 'Kaiserslautern', 'St Pauli', 'Osnabruck',
                               'Karlsruhe', 'Wehen', 'Magdeburg', 'Fortuna Dusseldorf', 'Hertha', 'Braunschweig', 'Holstein Kiel',
                               'Greuther Furth', 'Paderborn', 'Hansa Rostock', 'Nurnberg']),
        "Scottish League": sorted(['Aberdeen', 'Celtic', 'Dundee', 'Dundee United', 'Hearts', 'Hibernian', 'Kilmarnock',
                                    'Motherwell', 'Rangers', 'Ross County', 'St Johnstone', 'St Mirren']),
        "Belgium League": sorted(['Anderlecht', 'Antwerp', 'Beerschot VA', 'Cercle Brugge', 'Charleroi', 'Club Brugge',
                                  'Dender', 'Genk', 'Gent', 'Kortrijk', 'Mechelen', 'Oud-Heverlee Leuven', 'St Truiden',
                                  'St. Gilloise', 'Standard', 'Westerlo']),
        "Portuguese League": sorted(['Arouca', 'AVS', 'Benfica', 'Boavista', 'Casa Pia', 'Estoril', 'Estrela',
                                     'Famalicao', 'Farense', 'Gil Vicente', 'Guimaraes', 'Moreirense', 'Nacional',
                                     'Porto', 'Rio Ave', 'Santa Clara', 'Sp Braga', 'Sp Lisbon']),
        "Turkish League": sorted(['Ad. Demirspor', 'Alanyaspor', 'Antalyaspor', 'Besiktas', 'Bodrumspor', 'Buyuksehyr',
                                  'Eyupspor', 'Fenerbahce', 'Galatasaray', 'Gaziantep', 'Goztep', 'Hatayspor',
                                  'Kasimpasa', 'Kayserispor', 'Konyaspor', 'Rizespor', 'Samsunspor', 'Sivasspor',
                                  'Trabzonspor']),
        "Greece League": sorted(['AEK', 'Asteras Tripolis', 'Athens Kallithea', 'Atromitos', 'Lamia', 'Levadeiakos',
                                 'OFI Crete', 'Olympiakos', 'PAOK', 'Panathinaikos', 'Panetolikos',
                                 'Panserraikos', 'Volos NFC', 'Aris']),
    },
    'Others': {
        "Switzerland League": sorted(['Basel','Grasshoppers','Lausanne','Lugano','Luzern', 'Servette','Sion',
                                      'St. Gallen','Winterthur','Young Boys','Yverdon', 'Zurich']),
        "Denmark League": sorted(['Aarhus', 'Midtjylland', 'Nordsjaelland', 'Aalborg', 'Silkeborg', 'Sonderjyske',
                                  'Vejle', 'Randers FC', 'Viborg', 'Brondby', 'Lyngby', 'FC Copenhagen']),
        "Austria League": sorted(['Grazer AK', 'Salzburg', 'Altach', 'Tirol', 'Hartberg', 'LASK', 'Wolfsberger AC',
                                  'A. Klagenfurt', 'BW Linz', 'Austria Vienna', 'SK Rapid', 'Sturm Graz']),
        "Mexico League": sorted(['Puebla', 'Santos Laguna', 'Queretaro', 'Club Tijuana', 'Juarez', 'Atlas', 'Atl. San Luis',
                                 'Club America', 'Guadalajara Chivas', 'Toluca', 'Tigres UANL', 'Necaxa', 'Cruz Azul', 'Mazatlan FC',
                                 'UNAM Pumas', 'Club Leon', 'Pachuca', 'Monterrey']),
        "Russia League": sorted(['Lokomotiv Moscow', 'Akron Togliatti', 'Krylya Sovetov', 'Zenit', 'Dynamo Moscow', 'Fakel Voronezh',
                                 'FK Rostov', 'CSKA Moscow', 'Orenburg', 'Spartak Moscow', 'Akhmat Grozny', 'Krasnodar', 'Khimki', 'Dynamo Makhachkala',
                                 'Pari NN', 'Rubin Kazan']),
        "Romania League": sorted(['Farul Constanta', 'Unirea Slobozia', 'FC Hermannstadt', 'Univ. Craiova', 'Sepsi Sf. Gheorghe', 'Poli Iasi', 'UTA Arad',
                                 'FC Rapid Bucuresti', 'FCSB', 'U. Cluj', 'CFR Cluj', 'Din. Bucuresti', 'FC Botosani', 'Otelul', 'Petrolul', 'Gloria Buzau'])
    }
}


class Command(BaseCommand):
    help = 'Populate leagues and teams from hardcoded data structure'

    def handle(self, *args, **options):
        total_leagues = 0
        total_teams = 0
        
        for category, leagues_dict in LEAGUES_BY_CATEGORY.items():
            for league_name, teams_list in leagues_dict.items():
                # Create or get league
                league, created = League.objects.get_or_create(
                    name=league_name,
                    defaults={
                        'category': category,
                        'country': self._get_country_from_league(league_name)
                    }
                )
                if created:
                    total_leagues += 1
                    self.stdout.write(f"Created league: {league_name}")
                
                # Create teams for this league
                for team_name in teams_list:
                    team, created = Team.objects.get_or_create(
                        name=team_name,
                        defaults={
                            'league': league,
                            'country': league.country
                        }
                    )
                    if created:
                        total_teams += 1
                    else:
                        # Update existing team's league if it changed
                        if team.league != league:
                            team.league = league
                            team.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\n[OK] Populated leagues and teams successfully!\n"
                f"  - New Leagues: {total_leagues}\n"
                f"  - New Teams: {total_teams}\n"
                f"  - Total Leagues: {League.objects.count()}\n"
                f"  - Total Teams: {Team.objects.count()}"
            )
        )
    
    def _get_country_from_league(self, league_name):
        """Infer country from league name."""
        country_map = {
            'Premier League': 'England',
            'English Championship': 'England',
            'Serie A': 'Italy',
            'Serie B': 'Italy',
            'Ligue1': 'France',
            'Ligue2': 'France',
            'La Liga': 'Spain',
            'La Liga2': 'Spain',
            'Eredivisie': 'Netherlands',
            'Bundesliga': 'Germany',
            'Bundesliga2': 'Germany',
            'Scottish League': 'Scotland',
            'Belgium League': 'Belgium',
            'Portuguese League': 'Portugal',
            'Turkish League': 'Turkey',
            'Greece League': 'Greece',
            'Switzerland League': 'Switzerland',
            'Denmark League': 'Denmark',
            'Austria League': 'Austria',
            'Mexico League': 'Mexico',
            'Russia League': 'Russia',
            'Romania League': 'Romania',
        }
        return country_map.get(league_name, '')

