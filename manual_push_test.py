import os
import sys
import django
import requests
import base64
from datetime import datetime

# Setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from django.conf import settings
from predictor.auth_views import get_mpesa_access_token

def manual_stk_push(phone_number, amount=10):
    print(f"--- STARTING MANUAL STK PUSH TEST TO {phone_number} ---")
    
    # 1. Check Token
    access_token = get_mpesa_access_token()
    if not access_token:
        print("[FAIL] Could not get Access Token. Check Consumer Key/Secret.")
        return

    print(f"[PASS] Access Token Obtained")

    # 2. Prepare Payload
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password_str = settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp
    password = base64.b64encode(password_str.encode()).decode()
    
    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerBuyGoodsOnline",  # Till Number
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://leon-football.com/api/mpesa/callback/",
        "AccountReference": "TEST_MANUAL",
        "TransactionDesc": "Manual Test"
    }
    
    print("\n--- PAYLOAD ---")
    print(f"Shortcode: {payload['BusinessShortCode']}")
    print(f"Type: {payload['TransactionType']}")
    print(f"Phone: {payload['PhoneNumber']}")
    print("----------------")

    # 3. Send Request
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    print("\nSending request to Safaricom...")
    response = requests.post(settings.MPESA_STK_PUSH_URL, json=payload, headers=headers)
    
    print(f"\nResponse Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('ResponseCode') == '0':
            print("\n[SUCCESS] STK Push Sent Successfully!")
            print("CHECK YOUR PHONE NOW.")
        else:
            print(f"\n[FAIL] Safaricom Error: {data.get('CustomerMessage')}")
    else:
        print("\n[FAIL] HTTP Request Failed")

if __name__ == "__main__":
    # Use the number from the logs
    manual_stk_push("254759337926", amount=5)
