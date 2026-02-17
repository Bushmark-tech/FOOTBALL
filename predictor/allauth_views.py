"""
Custom allauth views with rate limiting and bot protection.
"""
from allauth.account.views import SignupView
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
import logging

logger = logging.getLogger(__name__)


@method_decorator(ratelimit(key='ip', rate='3/h', block=True), name='dispatch')
class RateLimitedSignupView(SignupView):
    """
    Custom signup view with rate limiting to prevent bot abuse.
    Limits signups to 3 per hour per IP address.
    """
    
    def form_valid(self, form):
        """
        Additional validation before signup
        """
        # Honeypot check
        if self.request.POST.get('website'):
            logger.warning(f"Bot signup blocked via honeypot: {form.cleaned_data.get('email')}")
            # Silently redirect without creating account
            from django.shortcuts import redirect
            return redirect('account_signup')
        
        return super().form_valid(form)
