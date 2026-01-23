import os
import requests
import base64
from datetime import datetime
from dotenv import load_dotenv

# Load .env
load_dotenv()

def get_mpesa_access_token():
    url = 'https://api.safaricom.co.ke/oauth/v1/generate'
    params = {'grant_type': 'client_credentials'}
    key = os.getenv('MPESA_CONSUMER_KEY')
    secret = os.getenv('MPESA_CONSUMER_SECRET')
    
    auth = base64.b64encode(f"{key}:{secret}".encode()).decode()
    headers = {'Authorization': f'Basic {auth}'}
    
    print(f"DEBUG: Triggering OAuth request to {url}")
    response = requests.get(url, headers=headers, params=params)
    
    print(f"Token Response: {response.status_code}")
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print(f"Error: {response.text}")
        return None

def initiate_stk_push(phone_number, amount, checkout_id):
    access_token = get_mpesa_access_token()
    if not access_token:
        print("Failed to get access token")
        return

    url = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    shortcode = os.getenv('MPESA_SHORTCODE', '5699046')
    passkey = os.getenv('MPESA_PASSKEY')
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()
    
    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://leon-football.com/api/mpesa/callback/",
        "AccountReference": f"TEST{checkout_id}"[:12],
        "TransactionDesc": "Test Prompt"
    }
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    print("Initiating STK Push...")
    response = requests.post(url, json=payload, headers=headers)
    print(f"STK Push Response ({response.status_code}): {response.text}")

if __name__ == "__main__":
    test_number = "254707407759"
    initiate_stk_push(test_number, 1, "999")
