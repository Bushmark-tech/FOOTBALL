"""
Test Football-Data.org API Key
Tests if the API key is valid and fetches upcoming matches
"""
import requests
from datetime import datetime, timedelta

# Your API Key
API_KEY = 'df9fad9870db2a2f0cd9a7b9cb493e8f'
BASE_URL = 'https://api.football-data.org/v4'

def test_api_connection():
    """Test basic API connection"""
    print("=" * 60)
    print("[TEST 1] TESTING API CONNECTION")
    print("=" * 60)
    
    headers = {'X-Auth-Token': API_KEY}
    
    try:
        response = requests.get(f"{BASE_URL}/competitions", headers=headers)
        
        print(f"\n[OK] Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("[SUCCESS] API Key is VALID!")
            data = response.json()
            competitions = data.get('competitions', [])
            print(f"[SUCCESS] Found {len(competitions)} competitions available")
            
            print("\n[INFO] Available Competitions (First 10):")
            for comp in competitions[:10]:
                print(f"   - {comp['name']} ({comp['code']}) - ID: {comp['id']}")
            
            return True
        elif response.status_code == 401:
            print("[ERROR] API Key is INVALID or EXPIRED")
            return False
        elif response.status_code == 429:
            print("[WARNING] Rate limit exceeded - too many requests")
            return False
        else:
            print(f"[ERROR] Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Connection Error: {e}")
        return False

def test_upcoming_matches():
    """Test fetching upcoming matches"""
    print("\n" + "=" * 60)
    print("[TEST 2] TESTING UPCOMING MATCHES")
    print("=" * 60)
    
    headers = {'X-Auth-Token': API_KEY}
    today = datetime.now().date()
    date_to = today + timedelta(days=7)
    
    params = {
        'dateFrom': today.isoformat(),
        'dateTo': date_to.isoformat()
    }
    
    try:
        response = requests.get(f"{BASE_URL}/matches", headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            matches = data.get('matches', [])
            
            print(f"\n[SUCCESS] Found {len(matches)} upcoming matches in next 7 days")
            
            if matches:
                print("\n[INFO] Sample Upcoming Matches (First 5):\n")
                for i, match in enumerate(matches[:5], 1):
                    home = match['homeTeam']['name']
                    away = match['awayTeam']['name']
                    competition = match['competition']['name']
                    match_date = match['utcDate']
                    status = match['status']
                    
                    print(f"{i}. {competition}")
                    print(f"   {home} vs {away}")
                    print(f"   Date: {match_date}")
                    print(f"   Status: {status}")
                    print()
            else:
                print("\n⚠️  No matches found in the next 7 days")
            
            return True
        else:
            print(f"❌ Error fetching matches: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_todays_matches():
    """Test fetching today's matches"""
    print("\n" + "=" * 60)
    print("⚽ TESTING TODAY'S MATCHES")
    print("=" * 60)
    
    headers = {'X-Auth-Token': API_KEY}
    today = datetime.now().date()
    
    params = {
        'dateFrom': today.isoformat(),
        'dateTo': today.isoformat()
    }
    
    try:
        response = requests.get(f"{BASE_URL}/matches", headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            matches = data.get('matches', [])
            
            print(f"\n✅ Found {len(matches)} matches TODAY ({today})")
            
            if matches:
                print("\n📍 Today's Matches:\n")
                for i, match in enumerate(matches, 1):
                    home = match['homeTeam']['name']
                    away = match['awayTeam']['name']
                    competition = match['competition']['name']
                    match_time = datetime.fromisoformat(match['utcDate'].replace('Z', '+00:00'))
                    status = match['status']
                    
                    print(f"{i}. {competition}")
                    print(f"   {home} vs {away}")
                    print(f"   Time: {match_time.strftime('%H:%M UTC')}")
                    print(f"   Status: {status}")
                    print()
            else:
                print("\n⚠️  No matches scheduled for today")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_premier_league():
    """Test fetching Premier League matches specifically"""
    print("\n" + "=" * 60)
    print("🏆 TESTING PREMIER LEAGUE MATCHES")
    print("=" * 60)
    
    headers = {'X-Auth-Token': API_KEY}
    
    # Premier League ID = 2021
    try:
        response = requests.get(
            f"{BASE_URL}/competitions/PL/matches",
            headers=headers,
            params={'status': 'SCHEDULED'}
        )
        
        if response.status_code == 200:
            data = response.json()
            matches = data.get('matches', [])
            
            print(f"\n✅ Found {len(matches)} scheduled Premier League matches")
            
            if matches:
                print("\n⚽ Premier League Upcoming Matches (First 5):\n")
                for i, match in enumerate(matches[:5], 1):
                    home = match['homeTeam']['name']
                    away = match['awayTeam']['name']
                    match_date = match['utcDate']
                    
                    print(f"{i}. {home} vs {away}")
                    print(f"   Date: {match_date}")
                    print()
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            if response.status_code == 403:
                print("⚠️  Premier League might not be available in free tier")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("FOOTBALL-DATA.ORG API TEST SUITE")
    print("=" * 60)
    print(f"\nAPI Key: {API_KEY[:10]}...{API_KEY[-10:]}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    test1 = test_api_connection()
    
    if test1:
        test2 = test_todays_matches()
        test3 = test_upcoming_matches()
        test4 = test_premier_league()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ API Connection: {'PASSED' if test1 else 'FAILED'}")
        print(f"✅ Today's Matches: {'PASSED' if test2 else 'FAILED'}")
        print(f"✅ Upcoming Matches: {'PASSED' if test3 else 'FAILED'}")
        print(f"✅ Premier League: {'PASSED' if test4 else 'FAILED'}")
        print("=" * 60)
        
        if all([test1, test2, test3]):
            print("\n🎉 ALL TESTS PASSED! Your API key is working perfectly!")
            print("\n💡 Next Steps:")
            print("   1. Add this API key to your Django settings")
            print("   2. Implement the upcoming matches feature")
            print("   3. Set up daily cron job to fetch matches")
        else:
            print("\n⚠️  Some tests failed. Check the details above.")
    else:
        print("\n❌ API connection failed. Cannot proceed with other tests.")

if __name__ == '__main__':
    main()
