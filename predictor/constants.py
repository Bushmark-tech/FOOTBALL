
LEAGUES_BY_CATEGORY = {
    'European Leagues': {
        "Premier League": sorted(['Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton', 'Burnley', 'Chelsea', 'Crystal Palace', 'Everton', 'Fulham', 'Leeds', 'Liverpool', 'Man City', 'Man United', 'Newcastle', "Nott'm Forest", 'Sunderland', 'Tottenham', 'West Ham', 'Wolves']),
        "English Championship": sorted(['Birmingham', 'Blackburn', 'Bristol City', 'Charlton', 'Coventry', 'Derby', 'Hull', 'Ipswich', 'Leicester', 'Middlesbrough', 'Millwall', 'Norwich', 'Oxford', 'Portsmouth', 'Preston', 'QPR', 'Sheffield United', 'Sheffield Weds', 'Southampton', 'Stoke', 'Swansea', 'Watford', 'West Brom', 'Wrexham']),
        "Serie A": sorted(['Atalanta', 'Bologna', 'Cagliari', 'Como', 'Cremonese', 'Fiorentina', 'Genoa', 'Inter', 'Juventus', 'Lazio', 'Lecce', 'Milan', 'Napoli', 'Parma', 'Pisa', 'Roma', 'Sassuolo', 'Torino', 'Udinese', 'Verona']),
        "Serie B": sorted(['Avellino', 'Bari', 'Carrarese', 'Catanzaro', 'Cesena', 'Empoli', 'Frosinone', 'Juve Stabia', 'Mantova', 'Modena', 'Monza', 'Padova', 'Palermo', 'Pescara', 'Reggiana', 'Sampdoria', 'Spezia', 'Sudtirol', 'Venezia', 'Virtus Entella']),
        "Ligue1": sorted(['Angers', 'Auxerre', 'Brest', 'Le Havre', 'Lens', 'Lille', 'Lorient', 'Lyon', 'Marseille', 'Metz', 'Monaco', 'Nantes', 'Nice', 'Paris FC', 'Paris SG', 'Rennes', 'Strasbourg', 'Toulouse']),
        "Ligue2": sorted(['Amiens', 'Annecy', 'Bastia', 'Boulogne', 'Clermont', 'Dunkerque', 'Grenoble', 'Guingamp', 'Laval', 'Le Mans', 'Montpellier', 'Nancy', 'Pau FC', 'Red Star', 'Reims', 'Rodez', 'St Etienne', 'Troyes']),
        "La Liga": sorted(['Alaves', 'Ath Bilbao', 'Ath Madrid', 'Barcelona', 'Betis', 'Celta', 'Elche', 'Espanol', 'Getafe', 'Girona', 'Levante', 'Mallorca', 'Osasuna', 'Oviedo', 'Real Madrid', 'Sevilla', 'Sociedad', 'Valencia', 'Vallecano', 'Villarreal']),
        "La Liga2": sorted(['Albacete', 'Almeria', 'Andorra', 'Burgos', 'Cadiz', 'Castellon', 'Ceuta', 'Cordoba', 'Cultural Leonesa', 'Eibar', 'Granada', 'Huesca', 'La Coruna', 'Las Palmas', 'Leganes', 'Malaga', 'Mirandes', 'Santander', 'Sociedad B', 'Sp Gijon', 'Valladolid', 'Zaragoza']),
        "Eredivisie": sorted(['AZ Alkmaar', 'Ajax', 'Excelsior', 'Feyenoord', 'For Sittard', 'Go Ahead Eagles', 'Groningen', 'Heerenveen', 'Heracles', 'NAC Breda', 'Nijmegen', 'PSV Eindhoven', 'Sparta Rotterdam', 'Telstar', 'Twente', 'Utrecht', 'Volendam', 'Zwolle']),
        "Bundesliga": sorted(['Augsburg', 'Bayern Munich', 'Dortmund', 'Ein Frankfurt', 'FC Koln', 'Freiburg', 'Hamburg', 'Heidenheim', 'Hoffenheim', 'Leverkusen', "M'gladbach", 'Mainz', 'RB Leipzig', 'St Pauli', 'Stuttgart', 'Union Berlin', 'Werder Bremen', 'Wolfsburg']),
        "Bundesliga2": sorted(['Bielefeld', 'Bochum', 'Braunschweig', 'Darmstadt', 'Dresden', 'Elversberg', 'Fortuna Dusseldorf', 'Greuther Furth', 'Hannover', 'Hertha', 'Holstein Kiel', 'Kaiserslautern', 'Karlsruhe', 'Magdeburg', 'Nurnberg', 'Paderborn', 'Preußen Münster', 'Schalke 04']),
        "Scottish League": sorted(['Aberdeen', 'Celtic', 'Dundee', 'Dundee United', 'Falkirk', 'Hearts', 'Hibernian', 'Kilmarnock', 'Livingston', 'Motherwell', 'Rangers', 'St Mirren']),
        "Belgium League": sorted(['Anderlecht', 'Antwerp', 'Cercle Brugge', 'Charleroi', 'Club Brugge', 'Dender', 'Genk', 'Gent', 'Mechelen', 'Oud-Heverlee Leuven', 'RAAL La Louviere', 'St Truiden', 'St. Gilloise', 'Standard', 'Waregem', 'Westerlo']),
        "Portuguese League": sorted(['AVS', 'Alverca', 'Arouca', 'Benfica', 'Casa Pia', 'Estoril', 'Estrela', 'Famalicao', 'Gil Vicente', 'Guimaraes', 'Moreirense', 'Nacional', 'Porto', 'Rio Ave', 'Santa Clara', 'Sp Braga', 'Sp Lisbon', 'Tondela']),
        "Turkish League": sorted(['Alanyaspor', 'Antalyaspor', 'Besiktas', 'Buyuksehyr', 'Eyupspor', 'Fenerbahce', 'Galatasaray', 'Gaziantep', 'Genclerbirligi', 'Goztep', 'Karagumruk', 'Kasimpasa', 'Kayserispor', 'Kocaelispor', 'Konyaspor', 'Rizespor', 'Samsunspor', 'Trabzonspor']),
        "Greece League": sorted(['AEK', 'Aris', 'Asteras Tripolis', 'Atromitos', 'Kifisia', 'Larisa', 'Levadeiakos', 'OFI Crete', 'Olympiakos', 'PAOK', 'Panathinaikos', 'Panetolikos', 'Panserraikos', 'Volos NFC']),
    },
    'Others': {
        "Switzerland League": sorted(['Basel', 'Grasshoppers', 'Lausanne', 'Lugano', 'Luzern', 'Servette', 'Sion', 'St. Gallen', 'Thun', 'Winterthur', 'Young Boys', 'Zurich']),
        "Denmark League": sorted(['Aarhus', 'Brondby', 'FC Copenhagen', 'Fredericia', 'Midtjylland', 'Nordsjaelland', 'Odense', 'Randers FC', 'Silkeborg', 'Sonderjyske', 'Vejle', 'Viborg']),
        "Austria League": sorted(['Altach', 'Austria Vienna', 'BW Linz', 'Grazer AK', 'Hartberg', 'LASK', 'Ried', 'SK Rapid', 'Salzburg', 'Sturm Graz', 'Tirol', 'Wolfsberger AC']),
        "Mexico League": sorted(['Atl. San Luis', 'Atlas', 'Club America', 'Club Leon', 'Club Tijuana', 'Cruz Azul', 'Guadalajara Chivas', 'Juarez', 'Mazatlan FC', 'Monterrey', 'Necaxa', 'Pachuca', 'Puebla', 'Queretaro', 'Santos Laguna', 'Tigres UANL', 'Toluca', 'UNAM Pumas']),
        "Russia League": sorted(['Akhmat Grozny', 'Akron Togliatti', 'Baltika', 'CSKA Moscow', 'Dynamo Makhachkala', 'Dynamo Moscow', 'FK Rostov', 'Krasnodar', 'Krylya Sovetov', 'Lokomotiv Moscow', 'Orenburg', 'Pari NN', 'Rubin Kazan', 'Sochi', 'Spartak Moscow', 'Zenit']),
        "Romania League": sorted(['CFR Cluj', 'Csikszereda M. Ciuc', 'Din. Bucuresti', 'FC Arges', 'FC Botosani', 'FC Hermannstadt', 'FC Rapid Bucuresti', 'FCSB', 'Farul Constanta', 'Metaloglobus Bucharest', 'Otelul', 'Petrolul', 'U. Cluj', 'UTA Arad', 'Unirea Slobozia', 'Univ. Craiova'])
    }
}
