import requests

try:
    url = "https://leon-football.com/wp-admin/setup-config.php"
    print(f"Testing {url}...")
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Content Snippet: {response.text[:100]}")
    
    if response.status_code == 403:
        print("✅ SUCCESS: Middleware is BLOCKING requests (403 Forbidden).")
    elif response.status_code == 404:
        print("❌ FAIL: Middleware is NOT working (404 Not Found).")
    else:
        print(f"⚠️ UNEXPECTED: {response.status_code}")

except Exception as e:
    print(f"Error: {e}")
