
import csv
import re
import os

raw_data = """
EPL
 Team  Code
0    Nott'm Forest   263
1        Brentford    64
2        Liverpool   220
3            Leeds   212
4           Fulham   148
5        Tottenham   365
6          Burnley    70
7   Crystal Palace   104
8         West Ham   398
9      Bournemouth    62
10       Newcastle   257
11      Man United   234
12         Arsenal    28
13        Brighton    67
14         Everton   129
15     Aston Villa    31
16        Man City   233
17         Chelsea    92
18          Wolves   403
19      Sunderland   358
Championship
Team  Code
0           Millwall   243
1            Swansea   359
2              Stoke   354
3          Blackburn    54
4       Bristol City    68
5         Birmingham    53
6           Charlton    89
7              Derby   110
8               Hull   183
9            Preston   300
10               QPR   302
11    Sheffield Weds   335
12         West Brom   397
13     Middlesbrough   241
14           Watford   394
15         Leicester   214
16           Norwich   262
17       Southampton   340
18  Sheffield United   334
19          Coventry   101
20           Ipswich   188
21            Oxford   274
22        Portsmouth   299
23           Wrexham   404
Scotland
Team  Code
0          Celtic    83
1       Hibernian   178
2      Livingston   221
3        Aberdeen     3
4      Kilmarnock   198
5          Hearts   173
6      Motherwell   250
7         Rangers   307
8       St Mirren   349
9   Dundee United   115
10         Dundee   114
11        Falkirk   135
Bundesliga 1
Team  Code
0       Stuttgart   356
1         Hamburg   168
2        St Pauli   350
3      Heidenheim   175
4   Bayern Munich    45
5      M'gladbach   228
6       Wolfsburg   402
7   Werder Bremen   396
8      Leverkusen   218
9        Freiburg   145
10       Dortmund   112
11  Ein Frankfurt   118
12   Union Berlin   374
13        FC Koln   134
14     Hoffenheim   179
15          Mainz   230
16       Augsburg    37
17     RB Leipzig   305
Bundesliga2
 Team  Code
0              Dresden   113
1        Holstein Kiel   180
2       Greuther Furth   164
3            Bielefeld    52
4               Bochum    57
5             Hannover   170
6            Karlsruhe   194
7            Darmstadt   106
8             Nurnberg   265
9           Schalke 04   330
10           Paderborn   278
11  Fortuna Dusseldorf   144
12              Hertha   177
13        Braunschweig    63
14      Kaiserslautern   192
15           Magdeburg   229
16          Elversberg   121
Serie A 
Team  Code
0         Pisa   293
1   Fiorentina   142
2        Parma   287
3         Roma   319
4     Cagliari    74
5      Udinese   371
6       Torino   364
7       Verona   382
8        Inter   186
9      Bologna    59
10       Milan   242
11   Cremonese   102
12    Juventus   191
13    Atalanta    32
14       Genoa   153
15       Lecce   210
16    Sassuolo   329
17       Lazio   207
18      Napoli   256
19        Como    97
Serie B
Team  Code
0   Virtus Entella   386
1          Venezia   381
2        Sampdoria   324
3           Empoli   122
4           Spezia   346
5        Frosinone   146
6          Pescara   291
7      Juve Stabia   190
8            Monza   248
9         Reggiana   312
10         Palermo   280
11          Modena   245
12            Bari    42
13        Sudtirol   357
14       Catanzaro    81
15          Cesena    85
16         Mantova   235
17       Carrarese    77
18        Avellino    39
19          Padova   279
Laliga
   Team  Code
0    Ath Bilbao    33
1         Elche   119
2     Vallecano   380
3         Celta    82
4      Valencia   377
5      Mallorca   232
6    Villarreal   384
7       Espanol   125
8        Girona   159
9    Ath Madrid    34
10        Betis    51
11       Alaves     8
12      Levante   217
13      Osasuna   270
14       Getafe   155
15  Real Madrid   309
16       Oviedo   273
17    Barcelona    41
18      Sevilla   333
19     Sociedad   338
Laliga2
Team  Code
0          Santander   328
1           Zaragoza   409
2            Almeria    13
3            Leganes   213
4         Las Palmas   205
5              Cadiz    72
6          La Coruna   202
7            Granada   162
8           Albacete     9
9             Malaga   231
10          Mirandes   244
11            Huesca   182
12          Sp Gijon   342
13        Valladolid   379
14             Eibar   117
15         Castellon    80
16        Sociedad B   339
17            Burgos    69
18           Andorra    19
19           Cordoba    99
20             Ceuta    86
21  Cultural Leonesa   105
French League 1
 Team  Code
0      Lorient   224
1     Le Havre   208
2     Paris FC   285
3      Auxerre    38
4         Lens   215
5       Monaco   246
6    Marseille   237
7       Angers    20
8        Brest    66
9         Nice   258
10       Lille   219
11  Strasbourg   355
12    Paris SG   286
13        Lyon   227
14      Nantes   255
15    Toulouse   366
16        Metz   240
17      Rennes   315
French League 2
Team  Code
0      Clermont    95
1      Guingamp   167
2         Nancy   254
3         Rodez   318
4       Le Mans   209
5        Troyes   369
6      Grenoble   163
7   Montpellier   247
8        Amiens    16
9         Reims   314
10   St Etienne   347
11       Pau FC   288
12    Dunkerque   116
13       Bastia    44
14       Annecy    22
15        Laval   206
16     Red Star   310
17     Boulogne    61
Eredivisie
Team  Code
0             Zwolle   410
1             Twente   370
2         AZ Alkmaar     2
3          Feyenoord   141
4           Heracles   176
5   Sparta Rotterdam   345
6          Groningen   165
7               Ajax     6
8        For Sittard   143
9            Utrecht   375
10        Heerenveen   174
11     PSV Eindhoven   276
12   Go Ahead Eagles   160
13          Nijmegen   259
14         Excelsior   130
15          Volendam   389
16         NAC Breda   252
17           Telstar   360
Belgium
Team  Code
0                  Genk   152
1         Cercle Brugge    84
2            St Truiden   351
3               Waregem   393
4            Anderlecht    18
5             Charleroi    88
6           Club Brugge    96
7              Mechelen   239
8              Standard   353
9                  Gent   154
10              Antwerp    24
11  Oud-Heverlee Leuven   272
12         St. Gilloise   352
13             Westerlo   399
14               Dender   108
15     RAAL La Louviere   304
Portugal
Team  Code
0       Benfica    49
1   Gil Vicente   157
2   Santa Clara   327
3      Sp Braga   341
4     Famalicao   136
5         Porto   298
6    Moreirense   249
7     Sp Lisbon   343
8     Guimaraes   166
9       Tondela   363
10      Rio Ave   316
11     Nacional   253
12       Arouca    27
13      Estoril   126
14     Casa Pia    79
15      Estrela   127
16          AVS     1
17      Alverca    15
Turkey
Team  Code
0   Genclerbirligi   151
1      Kayserispor   196
2        Konyaspor   200
3           Goztep   161
4        Kasimpasa   195
5       Fenerbahce   138
6         Besiktas    50
7       Alanyaspor     7
8       Buyuksehyr    71
9      Galatasaray   149
10        Rizespor   317
11     Trabzonspor   367
12     Antalyaspor    23
13       Gaziantep   150
14      Karagumruk   193
15      Samsunspor   325
16        Eyupspor   132
17     Kocaelispor   199
Greece
Team  Code
0               Aris    26
1         Olympiakos   267
2                AEK     0
3          Atromitos    36
4               PAOK   275
5        Panetolikos   282
6      Panathinaikos   281
7          Volos NFC   390
8   Asteras Tripolis    30
9             Larisa   204
10         OFI Crete   266
11       Levadeiakos   216
12           Kifisia   197
13      Panserraikos   284
"""

# Pattern to extract ID and Name
# Lines indicate: "Index  Name  Code"
# Regex: Start with digits, then spaces, then Name (spaces allowed), then spaces, then Code(digits) end
pattern = re.compile(r"^\d+\s+(.*?)\s+(\d+)$")

mapping = []

for line in raw_data.split('\n'):
    line = line.strip()
    if not line:
        continue
        
    match = pattern.match(line)
    if match:
        name = match.group(1).strip()
        code = match.group(2).strip()
        mapping.append((name, code))
    else:
        # Debug: print ignored lines to ensure we don't skip valid data
        if "Team" not in line and "Code" not in line and not any(league in line for league in ["EPL", "Serie", "Laliga", "Liga", "Bundesliga", "Scotland", "French", "Eredivisie", "Belgium", "Portugal", "Turkey", "Greece"]):
            print(f"Ignored: {line}")

# Write to CSV
try:
    with open('data/team_mapping.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Team', 'ID'])
        for name, code in mapping:
            writer.writerow([name, code])
    print(f"Successfully wrote {len(mapping)} teams to data/team_mapping.csv")
    
    # Validation: Check for duplicates
    ids = [code for _, code in mapping]
    names = [name for name, _ in mapping]
    
    unique_ids = len(set(ids))
    unique_names = len(set(names))
    total = len(mapping)
    
    print(f"Total Rows: {total}")
    print(f"Unique IDs: {unique_ids}")
    print(f"Unique Names: {unique_names}")
    
    if unique_ids < total:
        print("WARNING: Duplicate IDs exist.")
        # Find duplicates
        seen = set()
        dupes = set()
        for x in ids:
            if x in seen:
                dupes.add(x)
            seen.add(x)
        print(f"Duplicate IDs: {sorted(list(dupes))}")
        
except Exception as e:
    print(f"Error writing CSV: {e}")
