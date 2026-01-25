"""
M-Pesa Security Utilities

Provides security functions for M-Pesa payment integration:
- IP whitelist validation
- Callback signature verification
- Request validation
"""

import hashlib
import hmac
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

MPESA_ALLOWED_IPS = [
    '196.201.214.200',
    '196.201.214.206',
    '196.201.214.207',
    '196.201.214.208',
    '196.201.213.114',
    '196.201.213.44',
    '196.201.212.127',
    '196.201.212.128',
    '196.201.212.129',
    '196.201.212.132',
    '196.201.212.136',
    '196.201.212.138',
    '196.201.212.74',
    '196.201.212.69',
    # Add more M-Pesa IPs as needed
]





def get_client_ip(request):
    """
    Get the client's IP address from the request.
    
    Handles X-Forwarded-For header for proxied requests.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def validate_mpesa_ip(request):
    """
    Validate that the request comes from an allowed M-Pesa IP address.
    
    Args:
        request: Django request object
        
    Returns:
        bool: True if IP is allowed, False otherwise
    """
    client_ip = get_client_ip(request)
    
    # In development/sandbox mode, allow localhost
    if settings.MPESA_ENVIRONMENT == 'sandbox':
        if client_ip in ['127.0.0.1', 'localhost', '::1']:
            logger.info(f"M-Pesa IP validation: Allowing localhost in sandbox mode")
            return True
    
    # Check if IP is in allowed list
    is_allowed = client_ip in MPESA_ALLOWED_IPS
    
    if not is_allowed:
        logger.warning(f"M-Pesa IP validation failed: {client_ip} not in allowed list")
    else:
        logger.info(f"M-Pesa IP validation passed: {client_ip}")
    
    return is_allowed


def validate_mpesa_callback_signature(request, callback_data):
    """
    Validate M-Pesa callback signature to ensure authenticity.
    
    Note: M-Pesa uses different signature methods. Update this based on
    your specific M-Pesa integration requirements.
    
    Args:
        request: Django request object
        callback_data: Parsed callback data
        
    Returns:
        bool: True if signature is valid, False otherwise
    """
    try:
        # Get signature from request headers or callback data
        received_signature = request.META.get('HTTP_X_MPESA_SIGNATURE') or \
                           callback_data.get('signature')
        
        if not received_signature:
            logger.warning("M-Pesa callback signature missing")
            return False
        
        # Calculate expected signature
        # This is a placeholder - update with actual M-Pesa signature calculation
        # Example: HMAC-SHA256 of callback data with your secret key
        secret_key = settings.MPESA_PASSKEY
        
        # Create signature string (order matters - check M-Pesa docs)
        signature_string = f"{callback_data.get('TransactionID', '')}" \
                          f"{callback_data.get('Amount', '')}" \
                          f"{callback_data.get('PhoneNumber', '')}"
        
        expected_signature = hmac.new(
            secret_key.encode('utf-8'),
            signature_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        is_valid = hmac.compare_digest(received_signature, expected_signature)
        
        if not is_valid:
            logger.warning(f"M-Pesa signature validation failed")
        else:
            logger.info(f"M-Pesa signature validation passed")
        
        return is_valid
        
    except Exception as e:
        logger.error(f"Error validating M-Pesa signature: {e}")
        return False


def validate_mpesa_request(request):
    """
    Comprehensive M-Pesa request validation.
    
    Validates:
    - Request method is POST
    - Content type is JSON
    - IP address is allowed
    
    Args:
        request: Django request object
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check request method
    if request.method != 'POST':
        return False, "Invalid request method. Only POST allowed."
    
    # Check content type
    content_type = request.META.get('CONTENT_TYPE', '')
    if 'application/json' not in content_type:
        return False, "Invalid content type. Expected application/json."
    
    # Validate IP address
    if not validate_mpesa_ip(request):
        client_ip = get_client_ip(request)
        return False, f"Unauthorized IP address: {client_ip}"
    
    return True, None


def log_mpesa_transaction(transaction_type, data, status='received'):
    """
    Log M-Pesa transaction for audit trail.
    
    Args:
        transaction_type: Type of transaction (payment, callback, etc.)
        data: Transaction data
        status: Transaction status
    """
    logger.info(
        f"M-Pesa {transaction_type} - Status: {status} - "
        f"Data: {str(data)[:200]}..."  # Truncate for security
    )
