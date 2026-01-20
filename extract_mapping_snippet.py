# ==========================================
# MANUAL MAPPING CREATION
# ==========================================
# This script creates the Team Name -> ID mapping from manually provided data
# and saves it to a CSV file.

import pandas as pd
import os

# 1. Define the mapping dictionary based on provided data
team_mapping = {
    # Switzerland
    'Sion': 94,
    'St. Gallen': 98,
    'Thun': 102,
    'Zurich': 128,
    'Young Boys': 125,
    'Servette': 92,
    'Basel': 16,
    'Luzern': 61,
    'Lugano': 60,
    'Lausanne': 57,
    'Grasshoppers': 45,
    'Winterthur': 121,

    # Denmark
    'Midtjylland': 66,
    'Odense': 72,
    'Sonderjyske': 96,
    'Brondby': 17,
    'FC Copenhagen': 34,
    'Silkeborg': 93,
    'Randers FC': 82,
    'Aarhus': 3,
    'Nordsjaelland': 71,
    'Vejle': 117,
    'Viborg': 119,
    'Fredericia': 42,

    # Austria
    'SK Rapid': 86,
    'Tirol': 104,
    'LASK': 56,
    'Sturm Graz': 100,
    'Austria Vienna': 13,
    'Altach': 8,
    'Hartberg': 48,
    'Salzburg': 88,
    'Wolfsberger AC': 122,
    'Ried': 83,
    'BW Linz': 14,
    'Grazer AK': 46,

    # Mexico
    'Atlas': 12,
    'Atl. San Luis': 11,
    'Puebla': 79,
    'Pachuca': 75,
    'Necaxa': 70,
    'Tigres UANL': 103,
    'Toluca': 105,
    'Club America': 22,
    'Santos Laguna': 89,
    'Club Tijuana': 24,
    'UNAM Pumas': 110,
    'Club Leon': 23,
    'Cruz Azul': 26,
    'Guadalajara Chivas': 47,
    'Queretaro': 80,
    'Monterrey': 69,
    'Juarez': 52,
    'Mazatlan FC': 64,

    # Russia
    'FK Rostov': 39,
    'Spartak Moscow': 97,
    'Zenit': 127,
    'Krylya Sovetov': 55,
    'Akhmat Grozny': 6,
    'Lokomotiv Moscow': 59,
    'CSKA Moscow': 19,
    'Dynamo Moscow': 30,
    'Sochi': 95,
    'Krasnodar': 54,
    'Orenburg': 73,
    'Rubin Kazan': 85,
    'Pari NN': 76,
    'Baltika': 15,
    'Akron Togliatti': 7,
    'Dynamo Makhachkala': 29,

    # Romania
    'CFR Cluj': 18,
    'FCSB': 38,
    'FC Hermannstadt': 35,
    'FC Botosani': 33,
    'Din. Bucuresti': 28,
    'FC Arges': 32,
    'UTA Arad': 111,
    'Univ. Craiova': 114,
    'FC Rapid Bucuresti': 36,
    'Farul Constanta': 41,
    'U. Cluj': 109,
    'Petrolul': 77,
    'Otelul': 74,
    'Csikszereda M. Ciuc': 27,
    'Unirea Slobozia': 113,
    'Metaloglobus Bucharest': 65
}

try:
    # 2. Convert to DataFrame
    df_map = pd.DataFrame(list(team_mapping.items()), columns=['Team', 'ID'])
    
    # 3. Save to your desktop project folder
    #    Adjust path if necessary
    save_path = r'C:\Users\user\Desktop\Football djang\Football-main\data\team_mapping.csv'
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    df_map.to_csv(save_path, index=False)
    print(f"✅ Success! Mapping file saved to: {save_path}")
    print(f"   Total teams mapped: {len(df_map)}")
    print("\nFirst 5 Teams:")
    print(df_map.head())
    
except Exception as e:
    print(f"❌ Error during creation: {e}")

