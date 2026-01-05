
import csv
import re
import os
import pandas as pd

new_data = """
Switzerland
Team  Code
0           Sion    94
1     St. Gallen    98
2           Thun   102
3         Zurich   128
4     Young Boys   125
5       Servette    92
6          Basel    16
7         Luzern    61
8         Lugano    60
9       Lausanne    57
10  Grasshoppers    45
11    Winterthur   121
Denmark
 Team  Code
0     Midtjylland    66
1          Odense    72
2     Sonderjyske    96
3         Brondby    17
4   FC Copenhagen    34
5       Silkeborg    93
6      Randers FC    82
7          Aarhus     3
8   Nordsjaelland    71
9           Vejle   117
10         Viborg   119
11     Fredericia    42
Austria
Team  Code
0         SK Rapid    86
1            Tirol   104
2             LASK    56
3       Sturm Graz   100
4   Austria Vienna    13
5           Altach     8
6         Hartberg    48
7         Salzburg    88
8   Wolfsberger AC   122
9             Ried    83
10         BW Linz    14
11       Grazer AK    46
Mexico
Team  Code
0                Atlas    12
1        Atl. San Luis    11
2               Puebla    79
3              Pachuca    75
4               Necaxa    70
5          Tigres UANL   103
6               Toluca   105
7         Club America    22
8        Santos Laguna    89
9         Club Tijuana    24
10          UNAM Pumas   110
11           Club Leon    23
12           Cruz Azul    26
13  Guadalajara Chivas    47
14           Queretaro    80
15           Monterrey    69
16              Juarez    52
17         Mazatlan FC    64
Russia
 Team  Code
0            FK Rostov    39
1       Spartak Moscow    97
2                Zenit   127
3       Krylya Sovetov    55
4        Akhmat Grozny     6
5     Lokomotiv Moscow    59
6          CSKA Moscow    19
7        Dynamo Moscow    30
8                Sochi    95
9            Krasnodar    54
10            Orenburg    73
11         Rubin Kazan    85
12             Pari NN    76
13             Baltika    15
14     Akron Togliatti     7
15  Dynamo Makhachkala    29
Romania
Team  Code
0                 CFR Cluj    18
1                     FCSB    38
2          FC Hermannstadt    35
3              FC Botosani    33
4           Din. Bucuresti    28
5                 FC Arges    32
6                 UTA Arad   111
7            Univ. Craiova   114
8       FC Rapid Bucuresti    36
9          Farul Constanta    41
10                 U. Cluj   109
11                Petrolul    77
12                  Otelul    74
13     Csikszereda M. Ciuc    27
14         Unirea Slobozia   113
15  Metaloglobus Bucharest    65
"""

# Regex: Start with digits, then spaces, then Name (spaces allowed), then spaces, then Code(digits) end
pattern = re.compile(r"^\d+\s+(.*?)\s+(\d+)$")

new_mapping = []

for line in new_data.split('\n'):
    line = line.strip()
    if not line:
        continue
    match = pattern.match(line)
    if match:
        name = match.group(1).strip()
        code = match.group(2).strip()
        new_mapping.append((name, int(code)))
    else:
        # Check if it's a header line to ignore
        if "Team" not in line and "Code" not in line and len(line) > 3:
             # Just ignore headers
             pass

print(f"Parsed {len(new_mapping)} new teams.")

# Load existing mapping
existing_mapping = {}
if os.path.exists('data/team_mapping.csv'):
    try:
        df = pd.read_csv('data/team_mapping.csv')
        # Handle duplicate teams in existing mapping by keeping last? Or first?
        # We want to MERGE.
        # If 'Arsenal' exists, we keep it.
        # If 'Sion' (New) exists... we overwrite? Or keep?
        # User says "update this dictory". Usually implies overwrite or add.
        # I'll overwrite if name matches, otherwise add.
        
        # Convert to list of dicts
        for idx, row in df.iterrows():
            existing_mapping[row['Team']] = row['ID']
        
        print(f"Loaded {len(existing_mapping)} existing teams.")
    except Exception as e:
        print(f"Error loading existing mapping: {e}")

# Update with new data
count_added = 0
count_updated = 0

for name, code in new_mapping:
    if name in existing_mapping:
        if existing_mapping[name] != code:
            # Update ID?
            # User provided a code. I should trust user.
            existing_mapping[name] = code
            count_updated += 1
    else:
        existing_mapping[name] = code
        count_added += 1

print(f"Added {count_added} teams. Updated {count_updated} teams.")

# Write back
try:
    with open('data/team_mapping.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Team', 'ID'])
        # Sort by Name for neatness? Or just write.
        # Sorting by Name is good.
        for name in sorted(existing_mapping.keys()):
            writer.writerow([name, existing_mapping[name]])
    
    print("Successfully updated data/team_mapping.csv")
    print(f"Total Teams Now: {len(existing_mapping)}")
    
    # Check for Collisions again (just for info)
    all_ids = list(existing_mapping.values())
    unique_ids = len(set(all_ids))
    print(f"Unique IDs: {unique_ids}")
    if unique_ids < len(existing_mapping):
         print(f"WARNING: {len(existing_mapping) - unique_ids} ID collisions detected (likely intentional across leagues).")

except Exception as e:
    print(f"Error writing CSV: {e}")
