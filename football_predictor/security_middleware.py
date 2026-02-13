from django.http import HttpResponseForbidden

class ScannerBlockerMiddleware:
    """
    Middleware to block common bot scanners looking for PHP/WordPress files
    and returning 403 Forbidden immediately to save resources.
    """
    
    # List of substrings that immediately indicate a malicious scanner
    BLOCKED_PATTERNS = [
        '.php',             # Block all PHP requests (wp-login.php, index.php, etc)
        'wp-admin',         # WordPress admin
        'wp-content',       # WordPress content
        'wp-includes',      # WordPress includes
        'wordpress',        # WordPress folder
        '.env',             # Environment file scanners
        '.git',             # Git folder scanners
        '/b2b/',            # M-Pesa B2B scanners seen in docs
        'cgi-bin',          # Old script folder
        'bitrix',           # CMS scanner
        'manager',          # Admin panel scanner
        'setup-config',     # Setup files
        'xmlrpc',           # Common attack vector
        'actuator',         # Spring Boot scanner
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.lower()
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # 1. Block by User-Agent (Common Bot/Scanner tools)
        blocked_uas = [
            'python-requests',
            'python-aiohttp',
            'go-http-client',
            'node-fetch',
            'curl/',
            'wget',
        ]
        
        for ua in blocked_uas:
            if ua.lower() in user_agent.lower():
                return HttpResponseForbidden("Access Denied: Automated Tooling Not Allowed")
        
        # 2. Block by Path patterns
        for pattern in self.BLOCKED_PATTERNS:
            if pattern in path:
                return HttpResponseForbidden("Access Denied: Bot Activity Detected")

        response = self.get_response(request)
        return response
