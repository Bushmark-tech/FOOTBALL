
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

# List of disposable/temporary email domains to block during registration
# Updated periodically to combat bots and spam accounts
DISPOSABLE_EMAIL_DOMAINS = [
    '10minutemail.com', '10minutemail.net', '10minutemail.org', 
    '20minutemail.com', '60minutemail.com', '7daysmail.com',
    'armyspy.com', 'binkmail.com', 'bobmail.info', 'bugmenot.com',
    'burnermail.io', 'cachedmail.com', 'crazymailing.com', 'dayrep.com',
    'discard.email', 'dispostable.com', 'disroot.org', 'dropmail.me', 'einrot.com',
    'fakaitemp.com', 'fake-mail.net', 'fakeinbox.com', 'filzmail.com',
    'getairmail.com', 'getnada.com', 'grr.la', 'guerrillamail.biz', 'guerrillamail.com',
    'guerrillamail.de', 'guerrillamail.net', 'guerrillamail.org', 'hi2.in', 
    'incognitomail.org', 'inboxalias.com', 'instamail.org', 'jetable.org',
    'jourrapide.com', 'mail-fake.com', 'mail-temp.com', 'mail1a.com',
    'mailcatch.com', 'mailforspam.com', 'mailgenerator.net', 'mailinator.com',
    'mailnesia.com', 'mailnull.com', 'mailtemp.net', 'mailtothis.com', 'meltmail.com',
    'mintemail.com', 'moakt.com', 'mytrashmail.com', 'nada.ltd', 'net-temp.com',
    'notsharingmy.info', 'nowmymail.com', 'objectmail.com', 'pancakemail.com', 'pochta.la',
    'pookmail.com', 'proxypost.net', 'quickmail.nl', 'rhyta.com',
    'safetymail.info', 'sharklasers.com', 'slmail.me', 'spam4.me',
    'spamavert.com', 'spambob.com', 'spamcorptastic.com', 'spamgourmet.com', 'superrito.com',
    'teleworm.us', 'temp-mail.org', 'temp-mail.ru', 'tempmail.com', 'tempmail.de',
    'tempmail.net', 'tempmailaddress.com', 'tempmailgen.com', 'tempmailid.com',
    'tempmailplus.com', 'throwawaymail.com', 'trash-mail.at', 'trash-mail.com', 'trashmail.com',
    'trashmail.me', 'trashmail.net', 'vpost.me', 'vrtm.com',
    'yopmail.com', 'zapymail.com', 'zero-spam.com', 'zoidmail.com'
]
