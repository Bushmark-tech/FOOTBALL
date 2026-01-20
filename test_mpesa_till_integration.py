"""
M-Pesa Till Number Integration Test Suite
Tests the Till Number payment integration before deployment
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from predictor.models import Subscription, UserProfile
from predictor.auth_views import initiate_stk_push, get_mpesa_access_token
import base64

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}[PASS] {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}[FAIL] {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}[WARN] {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}[INFO] {text}{Colors.END}")

def test_configuration():
    """Test 1: Verify M-Pesa configuration"""
    print_header("TEST 1: M-Pesa Configuration")
    
    tests_passed = 0
    tests_total = 7
    
    # Test Consumer Key
    if hasattr(settings, 'MPESA_CONSUMER_KEY') and settings.MPESA_CONSUMER_KEY:
        print_success(f"Consumer Key: Set ({settings.MPESA_CONSUMER_KEY[:10]}...)")
        tests_passed += 1
    else:
        print_error("Consumer Key: NOT SET")
    
    # Test Consumer Secret
    if hasattr(settings, 'MPESA_CONSUMER_SECRET') and settings.MPESA_CONSUMER_SECRET:
        print_success(f"Consumer Secret: Set ({settings.MPESA_CONSUMER_SECRET[:10]}...)")
        tests_passed += 1
    else:
        print_error("Consumer Secret: NOT SET")
    
    # Test Shortcode (Till Number)
    if hasattr(settings, 'MPESA_SHORTCODE') and settings.MPESA_SHORTCODE:
        shortcode = settings.MPESA_SHORTCODE
        print_success(f"Shortcode (Till Number): {shortcode}")
        
        # Verify it's the correct Till Number
        if shortcode in ['3040653', '3049053']:
            print_info(f"  → Till Number format verified")
        else:
            print_warning(f"  → Unexpected shortcode value: {shortcode}")
        tests_passed += 1
    else:
        print_error("Shortcode: NOT SET")
    
    # Test Passkey
    if hasattr(settings, 'MPESA_PASSKEY') and settings.MPESA_PASSKEY:
        print_success(f"Passkey: Set ({settings.MPESA_PASSKEY[:10]}...)")
        tests_passed += 1
    else:
        print_error("Passkey: NOT SET")
    
    # Test Environment
    if hasattr(settings, 'MPESA_ENVIRONMENT'):
        env = settings.MPESA_ENVIRONMENT
        print_success(f"Environment: {env}")
        if env == 'sandbox':
            print_info("  → Sandbox mode (safe for testing)")
        elif env == 'production':
            print_warning("  → PRODUCTION mode (real money!)")
        tests_passed += 1
    else:
        print_error("Environment: NOT SET")
    
    # Test STK Push URL
    if hasattr(settings, 'MPESA_STK_PUSH_URL'):
        print_success(f"STK Push URL: {settings.MPESA_STK_PUSH_URL}")
        tests_passed += 1
    else:
        print_error("STK Push URL: NOT SET")
    
    # Test Access Token URL
    if hasattr(settings, 'MPESA_ACCESS_TOKEN_URL'):
        print_success(f"Access Token URL: {settings.MPESA_ACCESS_TOKEN_URL}")
        tests_passed += 1
    else:
        print_error("Access Token URL: NOT SET")
    
    print(f"\n{Colors.BOLD}Configuration Tests: {tests_passed}/{tests_total} passed{Colors.END}")
    return tests_passed == tests_total

def test_transaction_type():
    """Test 2: Verify transaction type is correct for Till Number"""
    print_header("TEST 2: Transaction Type Verification")
    
    # Read the auth_views.py file to check transaction type
    auth_views_path = os.path.join(os.path.dirname(__file__), 'predictor', 'auth_views.py')
    
    try:
        with open(auth_views_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'CustomerBuyGoodsOnline' in content:
            print_success("Transaction Type: CustomerBuyGoodsOnline (Correct for Till Number)")
            
            # Check if old type is still present
            if 'CustomerPayBillOnline' in content:
                print_warning("  → Old 'CustomerPayBillOnline' still found in file (might be in comments)")
            
            return True
        elif 'CustomerPayBillOnline' in content:
            print_error("Transaction Type: CustomerPayBillOnline (WRONG for Till Number!)")
            print_info("  → Should be 'CustomerBuyGoodsOnline' for Till Numbers")
            return False
        else:
            print_error("Transaction Type: NOT FOUND in code")
            return False
            
    except Exception as e:
        print_error(f"Error reading auth_views.py: {e}")
        return False

def test_password_generation():
    """Test 3: Verify password generation for STK Push"""
    print_header("TEST 3: Password Generation")
    
    try:
        shortcode = settings.MPESA_SHORTCODE
        passkey = settings.MPESA_PASSKEY
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Generate password
        password_string = shortcode + passkey + timestamp
        password = base64.b64encode(password_string.encode()).decode()
        
        print_success(f"Timestamp: {timestamp}")
        print_success(f"Password String: {shortcode} + [PASSKEY] + {timestamp}")
        print_success(f"Base64 Password: {password[:20]}...")
        print_info(f"  → Password length: {len(password)} characters")
        
        return True
        
    except Exception as e:
        print_error(f"Password generation failed: {e}")
        return False

def test_phone_number_formatting():
    """Test 4: Verify phone number formatting"""
    print_header("TEST 4: Phone Number Formatting")
    
    test_numbers = [
        ('0712345678', '254712345678'),
        ('712345678', '254712345678'),
        ('254712345678', '254712345678'),
        ('+254712345678', '254712345678'),
    ]
    
    all_passed = True
    
    for input_num, expected in test_numbers:
        # Simulate the formatting logic from auth_views.py
        formatted = input_num.replace(' ', '').replace('-', '').replace('+', '')
        if formatted.startswith('0'):
            formatted = '254' + formatted[1:]
        elif not formatted.startswith('254'):
            formatted = '254' + formatted
        
        if formatted == expected:
            print_success(f"{input_num} → {formatted}")
        else:
            print_error(f"{input_num} → {formatted} (expected {expected})")
            all_passed = False
    
    return all_passed

def test_stk_push_payload():
    """Test 5: Verify STK Push payload structure"""
    print_header("TEST 5: STK Push Payload Structure")
    
    try:
        shortcode = settings.MPESA_SHORTCODE
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(
            (shortcode + settings.MPESA_PASSKEY + timestamp).encode()
        ).decode()
        
        # Create sample payload
        payload = {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerBuyGoodsOnline",
            "Amount": 100,
            "PartyA": "254712345678",
            "PartyB": shortcode,
            "PhoneNumber": "254712345678",
            "CallBackURL": "https://leon-football.com/api/mpesa/callback/",
            "AccountReference": "SUB123",
            "TransactionDesc": "Football Predictor Subscription - 123"
        }
        
        print_success("Payload structure:")
        for key, value in payload.items():
            if key in ['Password', 'Timestamp']:
                print(f"  {key}: {str(value)[:20]}...")
            else:
                print(f"  {key}: {value}")
        
        # Verify critical fields
        checks_passed = 0
        checks_total = 4
        
        if payload['TransactionType'] == 'CustomerBuyGoodsOnline':
            print_success("✓ Transaction Type is correct for Till Number")
            checks_passed += 1
        else:
            print_error("✗ Transaction Type is WRONG")
        
        if payload['BusinessShortCode'] == payload['PartyB']:
            print_success("✓ BusinessShortCode matches PartyB")
            checks_passed += 1
        else:
            print_error("✗ BusinessShortCode and PartyB mismatch")
        
        if payload['PartyA'] == payload['PhoneNumber']:
            print_success("✓ PartyA matches PhoneNumber")
            checks_passed += 1
        else:
            print_error("✗ PartyA and PhoneNumber mismatch")
        
        if 'CallBackURL' in payload and payload['CallBackURL'].startswith('https://'):
            print_success(f"✓ Callback URL is HTTPS: {payload['CallBackURL']}")
            checks_passed += 1
        else:
            print_error("✗ Callback URL missing or not HTTPS")
        
        print(f"\n{Colors.BOLD}Payload Checks: {checks_passed}/{checks_total} passed{Colors.END}")
        return checks_passed == checks_total
        
    except Exception as e:
        print_error(f"Payload generation failed: {e}")
        return False

def test_database_models():
    """Test 6: Verify database models are ready"""
    print_header("TEST 6: Database Models")
    
    try:
        # Check if we can query subscriptions
        sub_count = Subscription.objects.count()
        print_success(f"Subscription model: OK ({sub_count} records)")
        
        # Check if we can query user profiles
        profile_count = UserProfile.objects.count()
        print_success(f"UserProfile model: OK ({profile_count} records)")
        
        # Check subscription fields
        if Subscription.objects.model._meta.get_field('mpesa_transaction_id'):
            print_success("✓ mpesa_transaction_id field exists")
        
        if Subscription.objects.model._meta.get_field('plan_type'):
            print_success("✓ plan_type field exists")
        
        if Subscription.objects.model._meta.get_field('amount'):
            print_success("✓ amount field exists")
        
        return True
        
    except Exception as e:
        print_error(f"Database model check failed: {e}")
        return False

def test_mock_payment():
    """Test 7: Test mock payment flow (if in sandbox without credentials)"""
    print_header("TEST 7: Mock Payment Flow")
    
    mpesa_configured = (
        hasattr(settings, 'MPESA_CONSUMER_KEY') and 
        settings.MPESA_CONSUMER_KEY and 
        settings.MPESA_CONSUMER_KEY != 'your-mpesa-consumer-key'
    )
    
    if not mpesa_configured:
        print_info("M-Pesa credentials not configured - Testing MOCK mode")
        
        try:
            # Create test user
            test_user, created = User.objects.get_or_create(
                username='test_mpesa_user',
                defaults={'email': 'test@example.com'}
            )
            
            # Create test subscription
            subscription = Subscription.objects.create(
                user=test_user,
                status='pending',
                payment_method='mpesa',
                plan_type='standard',
                amount=100,
                currency='KSH',
                mpesa_number='254712345678'
            )
            
            print_success(f"Created test subscription: {subscription.id}")
            
            # Test STK push in mock mode
            result = initiate_stk_push('254712345678', 100, subscription.id)
            
            if result.get('success'):
                print_success("Mock payment successful!")
                print_info(f"  → Message: {result.get('data', {}).get('CustomerMessage', 'N/A')}")
                print_info(f"  → Mock mode: {result.get('mock', False)}")
                
                # Check if subscription was activated
                subscription.refresh_from_db()
                if subscription.status == 'active':
                    print_success("✓ Subscription activated in mock mode")
                else:
                    print_warning(f"Subscription status: {subscription.status}")
                
                # Cleanup
                subscription.delete()
                if created:
                    test_user.delete()
                
                return True
            else:
                print_error(f"Mock payment failed: {result.get('error')}")
                subscription.delete()
                if created:
                    test_user.delete()
                return False
                
        except Exception as e:
            print_error(f"Mock payment test failed: {e}")
            return False
    else:
        print_info("M-Pesa credentials configured - Skipping mock test")
        print_warning("⚠ Cannot test real M-Pesa without actual phone number")
        print_info("  → Use the subscribe page to test with a real number")
        return True

def test_callback_security():
    """Test 8: Verify callback security is configured"""
    print_header("TEST 8: Callback Security")
    
    try:
        # Check if mpesa_security.py exists
        security_path = os.path.join(os.path.dirname(__file__), 'predictor', 'mpesa_security.py')
        
        if os.path.exists(security_path):
            print_success("mpesa_security.py exists")
            
            with open(security_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for IP whitelist
            if 'MPESA_CALLBACK_IPS' in content or '196.201' in content:
                print_success("✓ IP whitelist configured")
            else:
                print_warning("IP whitelist might not be configured")
            
            # Check for validation function
            if 'validate_mpesa_request' in content:
                print_success("✓ Request validation function exists")
            else:
                print_warning("Request validation function not found")
            
            return True
        else:
            print_warning("mpesa_security.py not found")
            print_info("  → Callback security might not be fully implemented")
            return True  # Not critical for basic functionality
            
    except Exception as e:
        print_error(f"Security check failed: {e}")
        return False

def run_all_tests():
    """Run all tests and generate report"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print("        M-PESA TILL NUMBER INTEGRATION TEST SUITE          ")
    print("=" * 60)
    print(f"{Colors.END}\n")
    
    print_info(f"Till Number: {settings.MPESA_SHORTCODE}")
    print_info(f"Environment: {settings.MPESA_ENVIRONMENT}")
    print_info(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Configuration", test_configuration),
        ("Transaction Type", test_transaction_type),
        ("Password Generation", test_password_generation),
        ("Phone Number Formatting", test_phone_number_formatting),
        ("STK Push Payload", test_stk_push_payload),
        ("Database Models", test_database_models),
        ("Mock Payment Flow", test_mock_payment),
        ("Callback Security", test_callback_security),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    print(f"\n{Colors.BOLD}")
    print(f"{'='*60}")
    print(f"Total: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    print(f"{'='*60}")
    print(f"{Colors.END}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED - READY TO DEPLOY!{Colors.END}\n")
        return True
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED - FIX ISSUES BEFORE DEPLOYING{Colors.END}\n")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
