import requests
import json

tests = [
    ('Chelsea', 'Brighton'),
    ('Man City', 'Liverpool'),
    ('Arsenal', 'Tottenham')
]

for home, away in tests:
    print(f'\n{home} vs {away}:')
    response = requests.post('http://127.0.0.1:8001/predict', json={'home_team': home, 'away_team': away})
    print(json.dumps(response.json(), indent=2))

