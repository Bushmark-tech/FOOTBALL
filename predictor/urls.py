from django.urls import path
from . import views

app_name = 'predictor'

urlpatterns = [
    path('', views.home, name='home'),
    path('predict/', views.predict, name='predict'),
    path('result/', views.result, name='result'),
    path('history/', views.history, name='history'),
    path('about/', views.about, name='about'),
    path('api/predict/', views.api_predict, name='api_predict'),
    path('api/teams/', views.get_teams_by_category, name='get_teams_by_category'),
    path('api/team-stats/', views.api_team_stats, name='api_team_stats'),
    path('api/head-to-head/', views.api_head_to_head, name='api_head_to_head'),
    path('api/market-odds/', views.api_market_odds, name='api_market_odds'),
    path('favicon.ico', views.favicon_view, name='favicon'),
    path('sw.js', views.favicon_view, name='sw_js'),  # Prevent 404 for service worker
]
