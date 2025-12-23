import requests
r = requests.post('http://127.0.0.1:8001/predict', json={'home_team': 'Basel', 'away_team': 'Young Boys', 'category': 'Others'}, timeout=60)
if r.status_code == 200:
    result = r.json()
    print(f"Basel vs Young Boys: {result.get('prediction')} ({result.get('confidence')*100:.1f}%)")
    print(f"Model: {result.get('model_type')}")
else:
    print(f"Error: {r.status_code}")

