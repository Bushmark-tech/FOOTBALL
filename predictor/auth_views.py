"""
Authentication and subscription views for the football predictor app.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
from .models import UserProfile, Subscription, Prediction
import logging
import requests
import base64
import json

from datetime import datetime

logger = logging.getLogger(__name__)


def check_subscription_status(user):
    """Check if user has active subscription or free matches available."""
    if not user.is_authenticated:
        return {'has_access': False, 'reason': 'not_authenticated'}
    
    # Admins and staff have unlimited access
    if user.is_superuser or user.is_staff:
        return {
            'has_access': True,
            'reason': 'admin_access',
            'limit': float('inf')
        }
    
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Get ALL active subscriptions (Stacking Logic)
    active_subscriptions = Subscription.objects.filter(
        user=user,
        status='active'
    )
    
    # Check if we have any valid active subscriptions
    valid_subs = [sub for sub in active_subscriptions if sub.is_active()]
    
    if valid_subs:
        total_remaining = 0
        plan_names = []
        
        for sub in valid_subs:
            # Plan names for display
            plan_names.append(sub.plan_type.title())
            # Calculate remaining for this specific sub
            remaining = sub.matches_limit - sub.matches_used
            if remaining > 0:
                total_remaining += remaining
                
        # Add the base "free" match to the subscriber's total if they haven't used it today
        # But wait, the user says "billed monthly ... if exhausted billed again"
        # Let's just use the subscription balance.
        
        if total_remaining <= 0:
             return {
                'has_access': False,
                'reason': 'limit_reached',
                'message': f'You have exhausted all matches in your {", ".join(plan_names)} plan(s). Please subscribe again to continue.'
            }

        return {
            'has_access': True,
            'reason': 'subscription',
            'remaining': total_remaining
        }
    
    # SECURITY FIX: Count ALL predictions (including archived) to prevent bypass
    # Users were archiving predictions to reset their count
    total_predictions = Prediction.objects.filter(user=user).count()
    
    # If user has exceeded free matches limit, block access
    if total_predictions >= profile.free_matches_limit:
        # Sync the count for accurate tracking
        if profile.free_matches_used < total_predictions:
            profile.free_matches_used = total_predictions
            profile.save()
            logger.info(f"User {user.username} has exceeded free matches limit. Total predictions: {total_predictions}/{profile.free_matches_limit}")
        return {
            'has_access': False,
            'reason': 'subscription_required',
            'profile': profile
        }
    
    # Sync free_matches_used with actual prediction count
    if total_predictions > profile.free_matches_used:
        profile.free_matches_used = total_predictions
        profile.save()
        logger.info(f"Synced free_matches_used for {user.username}: {profile.free_matches_used}/{profile.free_matches_limit}")
    
    # Check for free matches
    if profile.has_free_matches():
        return {
            'has_access': True,
            'reason': 'free_matches',
            'remaining': profile.get_remaining_free_matches(),
            'profile': profile
        }
    
    return {
        'has_access': False,
        'reason': 'subscription_required',
        'profile': profile
    }


def use_prediction_credit(user):
    """Use one prediction credit (free match or subscription)."""
    if not user.is_authenticated:
        return False
    
    # Admins and staff have unlimited access
    if user.is_superuser or user.is_staff:
        return True
    
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Check subscriptions (Stacking Logic)
    active_subscriptions = Subscription.objects.filter(
        user=user,
        status='active'
    )
    valid_subs = [sub for sub in active_subscriptions if sub.is_active()]
    
    if valid_subs:
        # Use oldest active subscription first
        for sub in sorted(valid_subs, key=lambda x: x.created_at):
            if sub.matches_used < sub.matches_limit:
                sub.matches_used += 1
                sub.save()
                return True
        return False  # All subscriptions exhausted
    
    # SECURITY FIX: Count ALL predictions (including archived) to prevent bypass
    total_predictions = Prediction.objects.filter(user=user).count()
    
    # If user has exceeded free matches limit, block access
    if total_predictions >= profile.free_matches_limit:
        # Sync the count for accurate tracking
        if profile.free_matches_used < total_predictions:
            profile.free_matches_used = total_predictions
            profile.save()
            logger.info(f"User {user.username} has exceeded free matches limit. Total predictions: {total_predictions}/{profile.free_matches_limit}")
        return False
    
    # Sync free_matches_used with actual prediction count
    if total_predictions > profile.free_matches_used:
        profile.free_matches_used = total_predictions
        profile.save()
        logger.info(f"Synced free_matches_used for {user.username}: {profile.free_matches_used}/{profile.free_matches_limit}")
    
    # Use free match
    if profile.has_free_matches():
        profile.use_free_match()
        return True
    
    return False


def subscription_required(view_func):
    """Decorator to check if user has subscription or free matches."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, 'Please login to make predictions.')
            return redirect('predictor:login')
        
        status = check_subscription_status(request.user)
        
        if not status['has_access']:
            messages.warning(request, 'You have used all your free matches. Please subscribe to continue.')
            return redirect('predictor:subscribe')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def login_view(request):
    """Login view with Google OAuth option and Email support."""
    # Get the redirection target
    next_url = request.GET.get('next', 'predictor:home')
    
    if request.user.is_authenticated:
        if next_url and next_url != 'predictor:home':
            return redirect(next_url)
        return redirect('predictor:home')
    
    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        next_url = request.POST.get('next', next_url)
        
        logger.info(f"Login attempt for: '{username_or_email}'")
        
        # Check if input is email or username
        user = None
        username_to_auth = username_or_email
        
        # Try to find user by email if input looks like an email
        if '@' in username_or_email:
            try:
                user_obj = User.objects.get(email__iexact=username_or_email)
                username_to_auth = user_obj.username
            except User.DoesNotExist:
                logger.warning(f"DEBUG: Email {username_or_email} not found in DB.")
                # If email lookup fails, we can't authenticate with it as a username usually
                # But we will let it fall through just in case
            except User.MultipleObjectsReturned:
                # This shouldn't happen with unique emails, but safety first
                user_obj = User.objects.filter(email__iexact=username_or_email).first()
                if user_obj:
                    username_to_auth = user_obj.username
        
        # Try to find user explicitly for debugging reasons
        if not user:
             try:
                 debug_user = User.objects.get(username=username_to_auth)
                 is_password_valid = debug_user.check_password(password)
                 logger.warning(f"DEBUG LOGIN FAILURE: User '{username_to_auth}' found. Active={debug_user.is_active}. PasswordValid={is_password_valid}")
             except User.DoesNotExist:
                 logger.warning(f"DEBUG LOGIN FAILURE: User '{username_to_auth}' NOT FOUND in DB.")

        user = authenticate(request, username=username_to_auth, password=password)
        
        if user:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            UserProfile.objects.get_or_create(user=user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            if next_url and next_url != 'predictor:home':
                if next_url.startswith('/'):
                    return redirect(next_url)
            return redirect('predictor:home')
        else:
            messages.error(request, 'Invalid email/username or password.')
    
    return render(request, 'predictor/login.html', {'next': next_url})


def register_view(request):
    """Registration view with Google Email restriction."""
    if request.user.is_authenticated:
        return redirect('predictor:home')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        
        # Validation: Google Email Only
        if not email or not email.strip().lower().endswith('@gmail.com'):
             messages.error(request, 'Registration is restricted to valid Google (@gmail.com) email addresses only.')
             return render(request, 'predictor/register.html')
        
        # Validation: Unique Email
        if User.objects.filter(email=email).exists():
             messages.error(request, 'This email address is already registered. Please login.')
             return render(request, 'predictor/register.html')

        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'predictor/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'predictor/register.html')
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Create user profile with 1 free match
            UserProfile.objects.create(user=user, free_matches_limit=1)
            
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome! Account created for {email}.')
            return redirect('predictor:home')
            
        except Exception as e:
            logger.error(f"Registration error: {e}")
            messages.error(request, 'An error occurred during registration.')
            return render(request, 'predictor/register.html')
    
    return render(request, 'predictor/register.html')


def logout_view(request):
    """Logout view that redirects to login page."""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('predictor:login')


def subscribe_view(request):
    """Subscription page with M-Pesa payment."""
    if not request.user.is_authenticated:
        messages.info(request, 'Please login to subscribe.')
        return redirect('predictor:login')
    
    try:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        status = check_subscription_status(request.user)
        
        # Get subscription prices from settings with defaults
        price_usd = getattr(settings, 'SUBSCRIPTION_PRICE_USD', 2.00)
        price_ksh = getattr(settings, 'SUBSCRIPTION_PRICE_KSH', 200.00)
        
        context = {
            'profile': profile,
            'status': status,
            'price_usd': price_usd,
            'price_ksh': price_ksh,
        }
        
        return render(request, 'predictor/subscribe.html', context)
    except Exception as e:
        logger.error(f"Error in subscribe_view: {e}")
        messages.error(request, 'An error occurred while loading the subscription page. Please try again.')
        return redirect('predictor:home')


@csrf_exempt
def initiate_mpesa_payment(request):
    """Initiate M-Pesa payment."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    logger.debug(f"DEBUG PAYMENT REQUEST: Body={request.body}")
    logger.debug(f"DEBUG PAYMENT REQUEST: Headers={request.content_type}")
    
    try:
        mpesa_number = request.POST.get('mpesa_number')
        currency = request.POST.get('currency', 'KSH')
        plan_type = request.POST.get('plan_type')
        
        if not mpesa_number and request.body:
             try:
                 import json
                 data = json.loads(request.body)
                 mpesa_number = data.get('mpesa_number')
                 currency = data.get('currency', 'KSH') # Default to KSH
                 plan_type = data.get('plan_type', 'standard')
             except json.JSONDecodeError:
                 pass
        
        if not mpesa_number:
            logger.debug("DEBUG: Number is missing after extraction")
            return JsonResponse({'error': 'M-Pesa number is required'}, status=400)
        
        # Validate M-Pesa number
        mpesa_number = mpesa_number.replace(' ', '').replace('-', '')
        if mpesa_number.startswith('0'):
            mpesa_number = '254' + mpesa_number[1:]
        elif not mpesa_number.startswith('254'):
            mpesa_number = '254' + mpesa_number
        
        logger.debug(f"DEBUG: Processed number: {mpesa_number}")

        if len(mpesa_number) != 12:
            logger.debug(f"DEBUG: Invalid Length {len(mpesa_number)}")
            return JsonResponse({'error': 'Invalid M-Pesa number format'}, status=400)
        
        # Determine amount based on plan_type (Security: Do not trust amount from client)
        # Determine amount based on plan_type and match limit
        plan_prices = getattr(settings, 'PLAN_PRICES', {'starter': 200, 'standard': 500, 'vip': 1000})
        plan_limits = getattr(settings, 'PLAN_MATCH_LIMITS', {'starter': 300, 'standard': 600, 'vip': 1500})
        
        if plan_type in plan_prices:
            amount = plan_prices[plan_type]
            matches_limit = plan_limits.get(plan_type, 0)
            currency = 'KSH'
        else:
            # Fallback
            plan_type = 'starter'
            amount = 200.00
            matches_limit = 300
            currency = 'KSH'
        
        # Create pending subscription
        subscription = Subscription.objects.create(
            user=request.user,
            status='pending',
            payment_method='mpesa',
            amount=amount,
            currency=currency,
            mpesa_number=mpesa_number,
            plan_type=plan_type,
            matches_limit=matches_limit
        )
        
        # Update user profile with M-Pesa number
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.mpesa_number = mpesa_number
        profile.save()
        
        # Initiate M-Pesa STK Push
        result = initiate_stk_push(request, mpesa_number, amount, subscription.id)
        
        if result.get('success'):
            # Use message from result (will be different for mock vs real)
            message = result.get('data', {}).get('CustomerMessage', 'Payment request sent to your phone. Please complete the payment.')
            
            return JsonResponse({
                'success': True,
                'message': message,
                'subscription_id': subscription.id,
                'is_mock': result.get('mock', False)
            })
        else:
            subscription.status = 'cancelled'
            subscription.save()
            return JsonResponse({
                'error': result.get('error', 'Failed to initiate payment')
            }, status=400)
    
    except Exception as e:
        logger.error(f"Error initiating M-Pesa payment: {e}")
        return JsonResponse({'error': 'Payment initiation failed'}, status=500)


def initiate_stk_push(request, phone_number, amount, subscription_id):
    """Initiate M-Pesa STK Push payment with mock mode for testing."""
    try:
        # Check if M-PESA credentials are configured
        mpesa_configured = (
            hasattr(settings, 'MPESA_CONSUMER_KEY') and 
            settings.MPESA_CONSUMER_KEY and 
            settings.MPESA_CONSUMER_KEY != 'your-mpesa-consumer-key'
        )
        
        # MOCK MODE: If M-PESA not configured, simulate successful payment
        if not mpesa_configured:
            logger.info(f"MOCK PAYMENT MODE: Simulating successful payment for subscription {subscription_id}")
            
            # Simulate a successful payment
            subscription = Subscription.objects.get(id=subscription_id)
            subscription.status = 'active'
            subscription.mpesa_transaction_id = f'MOCK-{subscription_id}-{datetime.now().strftime("%Y%m%d%H%M%S")}'
            
            # Use specific limit for this plan if set
            matches_limit = getattr(subscription, 'matches_limit', 0)
            subscription.activate(
                duration_days=getattr(settings, 'SUBSCRIPTION_DURATION_DAYS', 30),
                matches_limit=matches_limit
            )
            subscription.save()
            
            logger.info(f"MOCK PAYMENT: Subscription {subscription_id} activated successfully")
            
            return {
                'success': True, 
                'data': {
                    'ResponseCode': '0',
                    'ResponseDescription': 'Success (Mock Mode)',
                    'CheckoutRequestID': subscription.mpesa_transaction_id,
                    'CustomerMessage': 'Payment successful! (Test Mode - No actual charge)'
                },
                'mock': True
            }
        
        # REAL M-PESA MODE: Use actual M-PESA API
        # Get access token
        access_token = get_mpesa_access_token()
        if not access_token:
            return {'success': False, 'error': 'Failed to get access token'}
        
        # STK Push URL
        url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        if settings.MPESA_ENVIRONMENT == 'production':
            url = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        
        # Generate timestamp and password
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(
            (settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp).encode()
        ).decode()
        
        # Get callback URL dynamically from request
        from django.urls import reverse
        callback_path = reverse('predictor:mpesa_callback')
        callback_url = request.build_absolute_uri(callback_path)
        
        # Ensure HTTPS for production
        if not request.is_secure() and settings.MPESA_ENVIRONMENT == 'production':
            callback_url = callback_url.replace('http://', 'https://')
        
        logger.info(f"Using Callback URL: {callback_url}")
        
        # Request payload
        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": getattr(settings, 'MPESA_TRANSACTION_TYPE', 'CustomerPayBillOnline'),
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": settings.MPESA_TILL_NUMBER,
            "PhoneNumber": phone_number,
            "CallBackURL": callback_url,
            "AccountReference": f"SUB{subscription_id}",
            "TransactionDesc": f"Football Predictor Subscription - {subscription_id}"
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ResponseCode') == '0':
                # Update subscription with checkout request ID
                subscription = Subscription.objects.get(id=subscription_id)
                subscription.mpesa_transaction_id = data.get('CheckoutRequestID')
                subscription.save()
                
                return {'success': True, 'data': data}
            else:
                return {'success': False, 'error': data.get('CustomerMessage', 'Payment failed')}
        else:
            return {'success': False, 'error': f'Payment request failed: {response.status_code} - {response.text}'}
    
    except Exception as e:
        logger.error(f"Error in STK Push: {e}")
        return {'success': False, 'error': str(e)}


def get_mpesa_access_token():
    """Get M-Pesa OAuth access token."""
    try:
        url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
        if settings.MPESA_ENVIRONMENT == 'production':
            url = 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
        
        auth = base64.b64encode(
            f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}".encode()
        ).decode()
        
        headers = {'Authorization': f'Basic {auth}'}
        response = requests.get(url, headers=headers)
        
        logger.debug(f"DEBUG TOKEN RESPONSE: {response.status_code} {response.text}")
        logger.debug(f"DEBUG KEYS USING: {settings.MPESA_CONSUMER_KEY[:5]}...")

        if response.status_code == 200:
            return response.json().get('access_token')
        return None
    except Exception as e:
        logger.error(f"Error getting M-Pesa access token: {e}")
        return None


@csrf_exempt
def mpesa_callback(request):
    """
    Handle M-Pesa payment callback with security validation.
    
    Security features:
    - IP whitelist validation
    - Request method and content type validation
    - Transaction logging for audit trail
    """
    # Import security utilities
    from .mpesa_security import validate_mpesa_request, log_mpesa_transaction
    
    # Validate request (IP, method, content type)
    is_valid, error_message = validate_mpesa_request(request)
    if not is_valid:
        logger.warning(f"M-Pesa callback validation failed: {error_message}")
        log_mpesa_transaction('callback', {'error': error_message}, status='rejected')
        return JsonResponse({'error': error_message}, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Log incoming transaction
            log_mpesa_transaction('callback', data, status='received')
            
            result_code = data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
            checkout_request_id = data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
            
            # Validate required fields
            if result_code is None or not checkout_request_id:
                logger.error("M-Pesa callback missing required fields")
                return JsonResponse({'error': 'Invalid callback data'}, status=400)
            
            subscription = Subscription.objects.filter(
                mpesa_transaction_id=checkout_request_id
            ).first()
            
            if subscription:
                if result_code == 0:
                    # Payment successful
                    subscription.status = 'active'
                    subscription.activate(
                        duration_days=settings.SUBSCRIPTION_DURATION_DAYS,
                        matches_limit=subscription.matches_limit
                    )
                    
                    logger.info(f"M-Pesa payment successful for subscription {subscription.id}")
                    log_mpesa_transaction('callback', data, status='success')
                    
                    # Note: messages.success won't work here as there's no request context
                    # Consider using email notification or database flag instead
                else:
                    # Payment failed
                    subscription.status = 'cancelled'
                    logger.warning(f"M-Pesa payment failed for subscription {subscription.id}, code: {result_code}")
                    log_mpesa_transaction('callback', data, status='failed')
                
                subscription.save()
            else:
                logger.warning(f"M-Pesa callback for unknown subscription: {checkout_request_id}")
            
            return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})
            
        except json.JSONDecodeError:
            logger.error("M-Pesa callback: Invalid JSON")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Error processing M-Pesa callback: {e}")
            log_mpesa_transaction('callback', {'error': str(e)}, status='error')
            return JsonResponse({'error': 'Callback processing failed'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def verify_email(request, token):
    """
    Email verification endpoint.
    Verifies user email using the token sent via email.
    """
    try:
        # Find user profile with this token
        profile = UserProfile.objects.filter(verification_token=token).first()
        
        if not profile:
            messages.error(request, 'Invalid verification link.')
            return redirect('predictor:login')
        
        # Check if token is still valid (24 hours)
        if not profile.is_token_valid():
            messages.error(request, 
                'Verification link has expired. Please contact support or register again.')
            return redirect('predictor:login')
        
        # Check if already verified
        if profile.email_verified:
            messages.info(request, 'Email already verified. You can log in now.')
            return redirect('predictor:login')
        
        # Verify the email
        profile.email_verified = True
        profile.verification_token = None  # Clear token after use
        profile.token_created_at = None
        profile.save()
        
        # Activate the user account
        user = profile.user
        user.is_active = True
        user.save()
        
        # Send welcome email
        from .email_utils import send_welcome_email
        send_welcome_email(user)
        
        logger.info(f"Email verified for user: {user.username}")
        
        messages.success(request, 
            f'Email verified successfully! Welcome to Football Predictor Pro, {user.username}!')
        messages.info(request, 
            'You can now log in and start making predictions.')
        
        return redirect('predictor:login')
        
    except Exception as e:
        logger.error(f"Error in email verification: {e}")
        messages.error(request, 'An error occurred during verification. Please try again.')
        return redirect('predictor:login')
