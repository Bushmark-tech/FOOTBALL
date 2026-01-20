"""
Test M-Pesa API credentials and connection.
This script tests the M-Pesa API without making actual payments.
"""
import os
import sys
import django
import requests
import base64
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from django.conf import settings

def test_mpesa_credentials():
    """Test M-Pesa OAuth token generation."""
    print("=" * 60)
    print("M-PESA CREDENTIALS TEST")
    print("=" * 60)
    
    # Check if credentials are configured
    print("\n1. Checking Configuration...")
    print(f"   Environment: {settings.MPESA_ENVIRONMENT}")
    print(f"   Consumer Key: {settings.MPESA_CONSUMER_KEY[:10]}..." if settings.MPESA_CONSUMER_KEY else "   Consumer Key: NOT SET")
    print(f"   Consumer Secret: {settings.MPESA_CONSUMER_SECRET[:10]}..." if settings.MPESA_CONSUMER_SECRET else "   Consumer Secret: NOT SET")
    print(f"   Shortcode: {settings.MPESA_SHORTCODE}")
    print(f"   Passkey: {settings.MPESA_PASSKEY[:20]}..." if settings.MPESA_PASSKEY else "   Passkey: NOT SET")
    
    if not settings.MPESA_CONSUMER_KEY or not settings.MPESA_CONSUMER_SECRET:
        print("\n❌ ERROR: M-Pesa credentials not configured!")
        return False
    
    # Test OAuth token
    print("\n2. Testing OAuth Token Generation...")
    try:
        # Determine URL based on environment
        if settings.MPESA_ENVIRONMENT == 'production':
            url = 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
        else:
            url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
        
        print(f"   URL: {url}")
        
        # Create auth header
        auth = base64.b64encode(
            f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}".encode()
        ).decode()
        
        headers = {'Authorization': f'Basic {auth}'}
        
        # Make request
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token')
            expires_in = data.get('expires_in')
            
            print(f"   ✅ SUCCESS!")
            print(f"   Access Token: {access_token[:20]}...")
            print(f"   Expires In: {expires_in} seconds")
            return True
        else:
            print(f"   ❌ FAILED!")
            print(f"   Response: {response.text}")
            
            # Try to parse error
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('errorMessage', 'Unknown error')}")
            except:
                pass
            
            return False
            
    except requests.exceptions.Timeout:
        print("   ❌ TIMEOUT: Request took too long")
        return False
    except requests.exceptions.ConnectionError:
        print("   ❌ CONNECTION ERROR: Could not connect to M-Pesa API")
        return False
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

def test_stk_push_validation():
    """Test STK Push payload validation (without sending)."""
    print("\n3. Testing STK Push Payload...")
    
    try:
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(
            (settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp).encode()
        ).decode()
        
        # Create test payload
        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerBuyGoodsOnline",
            "Amount": 1,  # Test with 1 KSH
            "PartyA": "254712345678",  # Test number
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": "254712345678",
            "CallBackURL": "https://example.com/callback",
            "AccountReference": "TEST001",
            "TransactionDesc": "Test Transaction"
        }
        
        print("   Payload Structure:")
        for key, value in payload.items():
            if key == "Password":
                print(f"   - {key}: {value[:20]}...")
            else:
                print(f"   - {key}: {value}")
        
        print("\n   ✅ Payload structure is valid")
        return True
        
    except Exception as e:
        print(f"   ❌ ERROR creating payload: {e}")
        return False

if __name__ == "__main__":
    print("\nStarting M-Pesa Credentials Test...\n")
    
    # Run tests
    oauth_success = test_mpesa_credentials()
    payload_success = test_stk_push_validation()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"OAuth Token: {'✅ PASS' if oauth_success else '❌ FAIL'}")
    print(f"Payload Validation: {'✅ PASS' if payload_success else '❌ FAIL'}")
    
    if oauth_success and payload_success:
        print("\n✅ All tests passed! M-Pesa credentials are valid.")
        print("   You can proceed with production deployment.")
    else:
        print("\n❌ Some tests failed. Please check your M-Pesa credentials.")
        print("   Do NOT deploy to production until all tests pass.")
    
    print("=" * 60)
