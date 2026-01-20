import requests
import base64
from datetime import datetime
import json

# ==========================================
# DIRECT CREDENTIALS TEST FOR 0759337926
# ==========================================

# Credentials from your valid configuration
CONSUMER_KEY = "r2IXj8KBoM8QbFPPQTzdmPpmelanleTRobqzsZgbAGLf3i4t" 
CONSUMER_SECRET = "RUerdbN3pWXGbi3fp2PDicrrTQetWwtzhpZN34xGzITJR8qDhBAZx0aLNeVkaGrz"
PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e5b72ada1ed2c919"
SHORTCODE = "3049053"
PHONE_NUMBER = "254759337926"  # The number you provided

# URLs (SANDBOX)
TOKEN_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
STK_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

def run_test():
    print(f"\n--- TESTING REAL M-PESA STK PUSH ---")
    print(f"Target Phone: {PHONE_NUMBER}")
    print(f"Till Number: {SHORTCODE}")
    print(f"Environment: PRODUCTION")
    
    # 1. GET ACCESS TOKEN
    print(f"\n[1] Generating Access Token...")
    try:
        auth_str = f"{CONSUMER_KEY}:{CONSUMER_SECRET}"
        auth_bytes = auth_str.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            "Authorization": f"Basic {auth_b64}"
        }
        
        response = requests.get(TOKEN_URL, headers=headers)
        
        print(f"    Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"    FAILED TO GET TOKEN! Response: {response.text}")
            return
            
        access_token = response.json().get('access_token')
        print(f"    Token obtained successfully!")
        
    except Exception as e:
        print(f"    EXCEPTION: {e}")
        return

    # 2. SEND STK PUSH
    print(f"\n[2] Initiating STK Push...")
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password_str = SHORTCODE + PASSKEY + timestamp
    password_b64 = base64.b64encode(password_str.encode('ascii')).decode('ascii')
    
    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password_b64,
        "Timestamp": timestamp,
        "TransactionType": "CustomerBuyGoodsOnline", # Correct for Till Number
        "Amount": 1,  # Testing with 1 KSH
        "PartyA": PHONE_NUMBER,
        "PartyB": SHORTCODE,
        "PhoneNumber": PHONE_NUMBER,
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
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ResponseCode') == '0':
                print(f"\n    SUCCESS! Payment Request Sent.")
                print(f"    CHECK YOUR PHONE ({PHONE_NUMBER}) NOW!")
                print(f"    MerchantRequestID: {data.get('MerchantRequestID')}")
                print(f"    CheckoutRequestID: {data.get('CheckoutRequestID')}")
            else:
                print(f"\n    SAFARICOM ERROR: {data.get('CustomerMessage')}")
                
                # Common errors diagnosis
                msg = data.get('CustomerMessage', '')
                if 'authorized' in msg.lower():
                    print("    -> TIP: Check if your IP is whitelisted if this is a callback error.")
                elif 'initiator' in msg.lower():
                    print("    -> TIP: This error usually means the credentials don't match the Shortcode.")
        else:
            print(f"\n    REQUEST FAILED: {response.text}")
            
    except Exception as e:
        print(f"    EXCEPTION: {e}")

if __name__ == "__main__":
    run_test()
