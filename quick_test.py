"""Quick single prediction test to see timing."""
import requests
import time

url = "http://127.0.0.1:8001/predict"
payload = {"home_team": "Lugano", "away_team": "Luzern", "category": "Others"}

print("Making single prediction test...")
start = time.time()
response = requests.post(url, json=payload, timeout=60)
elapsed = time.time() - start

print(f"Status: {response.status_code}")
print(f"Time: {elapsed:.2f} seconds")
if response.status_code == 200:
    result = response.json()
    print(f"Result: {result.get('prediction')} - {result.get('model_type')}")
print("\n⚠️  Check the FastAPI console (where you ran 'python run_api.py')")
print("   Look for [PERF] timing breakdown to see which operations are slowest!")

