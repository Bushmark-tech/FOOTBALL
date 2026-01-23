import requests
import base64
from datetime import datetime
import json

# ==========================================
# DIRECT CREDENTIALS TEST FOR 0759337926
# ==========================================

import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# DIRECT CREDENTIALS TEST
# ==========================================

# Credentials from environment
CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET')
PASSKEY = os.environ.get('MPESA_PASSKEY')
SHORTCODE = os.environ.get('MPESA_SHORTCODE')
PHONE_NUMBER = "254707407759"  # The number you provided

# URLs
ENVIRONMENT = os.environ.get('MPESA_ENVIRONMENT', 'sandbox')
if ENVIRONMENT == 'production':
    TOKEN_URL = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    STK_URL = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
else:
    TOKEN_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    STK_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

def run_test():
    print(f"\n--- TESTING REAL M-PESA STK PUSH ---")
    print(f"Target Phone: {PHONE_NUMBER}")
    print(f"Till Number: {SHORTCODE}")
    print(f"Environment Configured: {ENVIRONMENT}")
    
    display_key = CONSUMER_KEY
    display_secret = CONSUMER_SECRET
    
    if not display_key or not display_secret:
        print("ERROR: Credentials not found in .env file!")
        return
        
    # Strip whitespace for local usage
    key_to_use = display_key.strip()
    secret_to_use = display_secret.strip()

    print(f"Key: {key_to_use[:5]}...{key_to_use[-5:]}")
    print(f"Secret: {secret_to_use[:5]}...{secret_to_use[-5:]}")

    # Helper to clean phone number
    formatted_phone = PHONE_NUMBER.strip().replace('+', '')
    if formatted_phone.startswith('0'):
        formatted_phone = '254' + formatted_phone[1:]
    
    # 1. GET ACCESS TOKEN
    print(f"\n[1] Generating Access Token...")
    
    def get_token(url, label):
        print(f"    Trying {label} URL: {url}")
        
        try:
            # Use requests built-in Basic Auth
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            # Debug the auth string
            import base64
            auth_str = f"{key_to_use}:{secret_to_use}"
            b64_auth = base64.b64encode(auth_str.encode()).decode()
            print(f"    Debug Auth Header: Basic {b64_auth[:10]}...{b64_auth[-10:]}")
            
            resp = requests.get(url, auth=(key_to_use, secret_to_use), timeout=30, headers=headers)
            print(f"    Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"    SUCCESS ({label})!")
                return resp.json().get('access_token')
            else:
                print(f"    FAILED.")
                print(f"    Headers: {resp.headers}")
                print(f"    Body: {resp.text}")
                return None
        except Exception as e:
            print(f"    EXCEPTION: {e}")
            return None

    # Try configured environment first
    access_token = get_token(TOKEN_URL, ENVIRONMENT.upper())
    
    # If failed, try swapping Key and Secret (Common mistake)
    if not access_token:
        print("\n    [Diagnostics] Token generation failed. Trying to SWAP Key and Secret...")
        # Swap
        temp = key_to_use
        key_to_use = secret_to_use
        secret_to_use = temp
        
        access_token = get_token(TOKEN_URL, ENVIRONMENT.upper() + " (SWAPPED)")
        
        if access_token:
            print("    [!] SUCCESS with SWAPPED credentials! Update your .env file.")
        else:
            # Swap back for next check
            temp = key_to_use
            key_to_use = secret_to_use
            secret_to_use = temp

    # If failed and likely due to env mismatch, try the other one
    if not access_token:
        print("\n    [Diagnostics] Token generation failed. Trying alternative environment...")
        fallback_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        if "sandbox" in TOKEN_URL:
            fallback_url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
            fallback_label = "PRODUCTION"
        else:
            fallback_label = "SANDBOX"
            
        access_token = get_token(fallback_url, fallback_label)
        if access_token:
            print(f"    WARNING: Credentials worked for {fallback_label}, but config says {ENVIRONMENT}!")
            # Update URLs for STK push
            global STK_URL
            if fallback_label == "SANDBOX":
                STK_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
            else:
                STK_URL = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    if not access_token:
        print("\n[!] FATAL: Could not generate access token in either environment.")
        return

    # 2. SEND STK PUSH
    print(f"\n[2] Initiating STK Push...")
    print(f"    Using URL: {STK_URL}")
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password_str = SHORTCODE + PASSKEY + timestamp
    password_b64 = base64.b64encode(password_str.encode('ascii')).decode('ascii')
    
    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password_b64,
        "Timestamp": timestamp,
        "TransactionType": "CustomerBuyGoodsOnline", # Correct for Till Number
        "Amount": 1, 
        "PartyA": formatted_phone,
        "PartyB": SHORTCODE,
        "PhoneNumber": formatted_phone,
        "CallBackURL": "https://leon-football.com/api/mpesa/callback/",
        "AccountReference": "TEST_DEBUG",
        "TransactionDesc": "Debug Test"
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(STK_URL, json=payload, headers=headers)
        
        print(f"    Status: {response.status_code}")
        print(f"    Response Raw: {response.text}")
        
    except Exception as e:
        print(f"    EXCEPTION: {e}")

if __name__ == "__main__":
    run_test()
