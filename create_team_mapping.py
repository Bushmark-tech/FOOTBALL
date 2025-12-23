"""
Create team ID mapping for football_data2.csv
Since the data uses encoded IDs, we'll create a mapping based on the teams we know
"""

# Teams from "Others" category in views.py
OTHERS_TEAMS = {
    "Switzerland League": ['Basel', 'Grasshoppers', 'Lausanne', 'Lugano', 'Luzern', 'Servette', 'Sion',
                          'St. Gallen', 'Winterthur', 'Young Boys', 'Yverdon', 'Zurich'],
    "Denmark League": ['Aarhus', 'Midtjylland', 'Nordsjaelland', 'Aalborg', 'Silkeborg', 'Sonderjyske',
                      'Vejle', 'Randers FC', 'Viborg', 'Brondby', 'Lyngby', 'FC Copenhagen'],
    "Austria League": ['Grazer AK', 'Salzburg', 'Altach', 'Tirol', 'Hartberg', 'LASK', 'Wolfsberger AC',
                      'A. Klagenfurt', 'BW Linz', 'Austria Vienna', 'SK Rapid', 'Sturm Graz'],
    "Mexico League": ['Puebla', 'Santos Laguna', 'Queretaro', 'Club Tijuana', 'Juarez', 'Atlas', 'Atl. San Luis',
                     'Club America', 'Guadalajara Chivas', 'Toluca', 'Tigres UANL', 'Necaxa', 'Cruz Azul', 'Mazatlan FC',
                     'UNAM Pumas', 'Club Leon', 'Pachuca', 'Monterrey'],
    "Russia League": ['Lokomotiv Moscow', 'Akron Togliatti', 'Krylya Sovetov', 'Zenit', 'Dynamo Moscow', 'Fakel Voronezh',
                     'FK Rostov', 'CSKA Moscow', 'Orenburg', 'Spartak Moscow', 'Akhmat Grozny', 'Krasnodar', 'Khimki', 'Dynamo Makhachkala',
                     'Pari NN', 'Rubin Kazan'],
    "Romania League": ['Farul Constanta', 'Unirea Slobozia', 'FC Hermannstadt', 'Univ. Craiova', 'Sepsi Sf. Gheorghe', 'Poli Iasi', 'UTA Arad',
                      'FC Rapid Bucuresti', 'FCSB', 'U. Cluj', 'CFR Cluj', 'Din. Bucuresti', 'FC Botosani', 'Otelul', 'Petrolul', 'Gloria Buzau']
}

# Create a flat list of all teams
all_teams = []
for league, teams in OTHERS_TEAMS.items():
    all_teams.extend(teams)

print(f"Total teams in Others category: {len(all_teams)}")
print(f"\nTeams by league:")
for league, teams in OTHERS_TEAMS.items():
    print(f"  {league}: {len(teams)} teams")

# Since we have 127 encoded IDs (0-126) and we have fewer teams in our list,
# the data likely contains more leagues/teams than we've defined
# Let's create a simple mapping strategy:

# Strategy: Use team name as key, assign sequential IDs
# This is a temporary mapping until we get the actual encoding

TEAM_NAME_TO_ID = {}
ID_TO_TEAM_NAME = {}

# Assign IDs sequentially
team_id = 0
for league, teams in sorted(OTHERS_TEAMS.items()):
    for team in sorted(teams):
        TEAM_NAME_TO_ID[team] = team_id
        ID_TO_TEAM_NAME[team_id] = team
        team_id += 1

print(f"\n{'='*70}")
print(f"Created mapping for {len(TEAM_NAME_TO_ID)} teams")
print(f"{'='*70}")

# Save to file
mapping_code = f'''"""
Team ID Mapping for football_data2.csv
Auto-generated mapping for Model 2 (Others category)
"""

# Team Name to ID mapping
TEAM_NAME_TO_ID = {TEAM_NAME_TO_ID}

# ID to Team Name mapping
ID_TO_TEAM_NAME = {ID_TO_TEAM_NAME}

def get_team_id(team_name):
    """Get encoded ID for a team name."""
    return TEAM_NAME_TO_ID.get(team_name)

def get_team_name(team_id):
    """Get team name for an encoded ID."""
    return ID_TO_TEAM_NAME.get(team_id)

def encode_team_name(team_name):
    """Encode team name to ID (alias for get_team_id)."""
    return get_team_id(team_name)

def decode_team_id(team_id):
    """Decode team ID to name (alias for get_team_name)."""
    return get_team_name(team_id)
'''

with open('predictor/team_mapping.py', 'w', encoding='utf-8') as f:
    f.write(mapping_code)

print("\nMapping saved to: predictor/team_mapping.py")
print("\nSample mappings:")
for i, (team, tid) in enumerate(list(TEAM_NAME_TO_ID.items())[:10]):
    print(f"  {team} → {tid}")

print("\n" + "="*70)
print("NOTE: This is a TEMPORARY mapping!")
print("The actual encoding in football_data2.csv may be different.")
print("We need to either:")
print("  1. Find the original encoding mapping file")
print("  2. Reverse-engineer from the data by analyzing patterns")
print("  3. Use a different approach (form-based predictions)")
print("="*70)

