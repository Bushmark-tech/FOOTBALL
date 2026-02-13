from django.urls import path
from . import views
from . import auth_views
from . import admin_views
from . import api_views

app_name = 'predictor'

urlpatterns = [
    path('', views.home, name='home'),
    path('predict/', views.predict, name='predict'),
    path('result/', views.result, name='result'),
    path('history/', views.history, name='history'),
    path('about/', views.about, name='about'),
    
    # ========== ADMIN DASHBOARD ==========
    path('admin/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/login/', views.redirect_to_login, name='admin_login_redirect'),
    
    # User Management
    path('admin/users/', admin_views.admin_users, name='admin_users'),
    path('admin/users/audit/', admin_views.admin_user_audit, name='admin_user_audit'),
    path('admin/security/action/', admin_views.admin_security_action, name='admin_security_action'),
    path('admin/users/<int:user_id>/', admin_views.admin_user_detail, name='admin_user_detail'),
    path('admin/users/<int:user_id>/action/', admin_views.admin_user_action, name='admin_user_action'),
    
    # Prediction Management
    path('admin/predictions/', admin_views.admin_predictions, name='admin_predictions'),
    path('admin/predictions/<int:prediction_id>/action/', admin_views.admin_prediction_action, name='admin_prediction_action'),
    
    # Billing & Subscriptions
    path('admin/billing/', admin_views.admin_billing, name='admin_billing'),
    path('admin/billing/<int:subscription_id>/action/', admin_views.admin_subscription_action, name='admin_subscription_action'),
    
    # Analytics & Reporting
    path('admin/analytics/', admin_views.admin_analytics, name='admin_analytics'),
    
    # System Control & Maintenance
    path('admin/system/', admin_views.admin_system, name='admin_system'),
    
    # Data Management
    path('admin/data/', admin_views.admin_data, name='admin_data'),
    path('admin/data/import/', admin_views.import_data, name='import_data'),
    path('admin/data/export/', admin_views.export_data, name='export_data'),
    path('admin/data/sync/', admin_views.sync_data, name='sync_data'),
    
    # API Endpoints
    path('admin/api/stats/', admin_views.admin_api_stats, name='admin_api_stats'),
    path('admin/email/debug/', admin_views.debug_email, name='debug_email'),
    
    # ========== AUTHENTICATION ==========
    path('login/', auth_views.login_view, name='login'),
    path('register/', auth_views.register_view, name='register'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('verify-email/<str:token>/', auth_views.verify_email, name='verify_email'),
    path('subscribe/', auth_views.subscribe_view, name='subscribe'),
    
    # ========== API ENDPOINTS ==========
    path('api/predict/', api_views.api_predict, name='api_predict'),
    path('api/teams/', api_views.get_teams_by_category, name='get_teams_by_category'),
    path('api/team-stats/', api_views.api_team_stats, name='api_team_stats'),
    path('api/head-to-head/', api_views.api_head_to_head, name='api_head_to_head'),
    path('api/market-odds/', api_views.api_market_odds, name='api_market_odds'),

    path('api/mpesa/payment/', auth_views.initiate_mpesa_payment, name='mpesa_payment'),
    path('api/mpesa/callback/', auth_views.mpesa_callback, name='mpesa_callback'),
    
    # Health Check
    path('health/', views.health_check, name='health_check'),
    path('init-db/', views.init_database, name='init_database'),  # Manual DB initialization
    
    path('favicon.ico', views.favicon_view, name='favicon'),
    path('sw.js', views.favicon_view, name='sw_js'),  # Prevent 404 for service worker
]
