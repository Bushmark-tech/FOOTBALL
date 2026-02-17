"""
URL configuration for football_predictor project.
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from django.views.generic.base import TemplateView
from predictor.password_reset_views import CustomPasswordResetView

from predictor.allauth_views import RateLimitedSignupView

urlpatterns = [
    path('system-core-database/', admin.site.urls),
    
    # Custom rate-limited signup (must come BEFORE allauth.urls)
    path('accounts/signup/', RateLimitedSignupView.as_view(), name='account_signup'),
    
    # Google OAuth and other allauth URLs
    path('accounts/', include('allauth.urls')),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    
    # Password Reset URLs (with custom logging)
    path('password_reset/', CustomPasswordResetView.as_view(
        extra_email_context={
            'domain': 'leon-football.com', 
            'protocol': 'https',
            'site_name': 'Football Predictor'
        }
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    path('', include('predictor.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


