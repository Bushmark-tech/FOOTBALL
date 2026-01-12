"""
Simple M-Pesa Till Number Pre-Deployment Check
Windows-compatible version without Unicode characters
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from django.conf import settings

print("\n" + "="*60)
print("  M-PESA TILL NUMBER - PRE-DEPLOYMENT CHECK")
print("="*60 + "\n")

# Check 1: Configuration
print("[1] M-PESA CONFIGURATION")
print("-" * 60)
print(f"Till Number (MPESA_SHORTCODE): {settings.MPESA_SHORTCODE}")
print(f"Environment: {settings.MPESA_ENVIRONMENT}")
print(f"Consumer Key: {'SET' if settings.MPESA_CONSUMER_KEY else 'NOT SET'}")
print(f"Consumer Secret: {'SET' if settings.MPESA_CONSUMER_SECRET else 'NOT SET'}")
print(f"Passkey: {'SET' if settings.MPESA_PASSKEY else 'NOT SET'}")

# Check 2: Till Number Verification
print("\n[2] TILL NUMBER VERIFICATION")
print("-" * 60)
expected_till = "3040653"
actual_till = settings.MPESA_SHORTCODE

if actual_till == expected_till:
    print(f"[PASS] Till Number matches: {actual_till}")
else:
    print(f"[WARN] Till Number mismatch!")
    print(f"  Expected: {expected_till}")
    print(f"  Actual: {actual_till}")
    print(f"  Note: Environment variable will override this default")

# Check 3: Transaction Type
print("\n[3] TRANSACTION TYPE CHECK")
print("-" * 60)
auth_views_path = os.path.join(os.path.dirname(__file__), 'predictor', 'auth_views.py')

try:
    with open(auth_views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'CustomerBuyGoodsOnline' in content:
        print("[PASS] Transaction Type: CustomerBuyGoodsOnline (Correct for Till)")
    else:
        print("[FAIL] Transaction Type: NOT FOUND or INCORRECT")
        
except Exception as e:
    print(f"[ERROR] Could not read auth_views.py: {e}")

# Check 4: URLs Configuration
print("\n[4] API URLS")
print("-" * 60)
print(f"STK Push URL: {settings.MPESA_STK_PUSH_URL}")
print(f"Access Token URL: {settings.MPESA_ACCESS_TOKEN_URL}")

# Check 5: Callback URL
print("\n[5] CALLBACK CONFIGURATION")
print("-" * 60)
print("Callback URL: https://leon-football.com/api/mpesa/callback/")
print("\nIMPORTANT: Register this URL in Safaricom Daraja Portal!")

# Check 6: Security
print("\n[6] SECURITY SETTINGS")
print("-" * 60)
security_file = os.path.join(os.path.dirname(__file__), 'predictor', 'mpesa_security.py')
if os.path.exists(security_file):
    print("[PASS] mpesa_security.py exists")
else:
    print("[WARN] mpesa_security.py not found")

# Summary
print("\n" + "="*60)
print("  DEPLOYMENT CHECKLIST")
print("="*60)

checklist = [
    ("Till Number set to 3040653", actual_till == expected_till),
    ("Transaction Type is CustomerBuyGoodsOnline", 'CustomerBuyGoodsOnline' in content),
    ("Consumer Key configured", bool(settings.MPESA_CONSUMER_KEY)),
    ("Consumer Secret configured", bool(settings.MPESA_CONSUMER_SECRET)),
    ("Passkey configured", bool(settings.MPESA_PASSKEY)),
    ("Environment set (sandbox/production)", bool(settings.MPESA_ENVIRONMENT)),
]

all_passed = True
for item, status in checklist:
    status_text = "[PASS]" if status else "[FAIL]"
    print(f"{status_text} {item}")
    if not status:
        all_passed = False

# Final verdict
print("\n" + "="*60)
if all_passed:
    print("STATUS: READY TO DEPLOY!")
    print("\nNext Steps:")
    print("1. Ensure Render environment variables are set correctly")
    print("2. Register callback URL in Daraja Portal")
    print("3. Whitelist M-Pesa IPs in your firewall")
    print("4. Test with a small payment first")
else:
    print("STATUS: ISSUES FOUND - FIX BEFORE DEPLOYING")
    print("\nPlease address the [FAIL] items above")

print("="*60 + "\n")

# Additional Info
print("QUICK REFERENCE:")
print("-" * 60)
print(f"Till Number: {expected_till}")
print(f"Transaction Type: CustomerBuyGoodsOnline")
print(f"Callback URL: https://leon-football.com/api/mpesa/callback/")
print(f"Environment: {settings.MPESA_ENVIRONMENT}")
print("\nM-Pesa Callback IPs to Whitelist:")
print("196.201.214.200, 196.201.214.206, 196.201.213.114")
print("196.201.214.207, 196.201.214.208, 196.201.213.44")
print("196.201.212.127-129, 196.201.212.136, 196.201.212.74, 196.201.212.69")
print("="*60 + "\n")
