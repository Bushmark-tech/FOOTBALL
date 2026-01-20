import os
import django
import sys
from datetime import timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings_production')
try:
    django.setup()
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth import get_user_model
from predictor.models import Prediction, Subscription, Match, Team, League

User = get_user_model()

def print_header(title):
    print(f"\n{'='*60}")
    print(f" {title.upper()}")
    print(f"{'='*60}")

def print_stat(label, value, extra=""):
    print(f"  {label:<25} : {str(value):<15} {extra}")

# --- Time ---
today = timezone.now().date()
week_ago = timezone.now() - timedelta(days=7)
month_ago = timezone.now() - timedelta(days=30)

# --- 1. USER METRICS ---
print_header("USER METRICS")
total_users = User.objects.count()
active_users = User.objects.filter(prediction__prediction_date__gte=week_ago).distinct().count()
new_users_month = User.objects.filter(date_joined__gte=month_ago).count()
new_users_week = User.objects.filter(date_joined__gte=week_ago).count()

# Google vs Email
try:
    from allauth.socialaccount.models import SocialAccount
    google_users = SocialAccount.objects.filter(provider='google').count()
except:
    google_users = 0
email_users = total_users - google_users

print_stat("Total Users", total_users)
print_stat("Active Users (7d)", active_users)
print_stat("New Users (30d)", new_users_month)
print_stat("New Users (7d)", new_users_week)
print_stat("Acquisition", f"{email_users} Email / {google_users} Google")

# --- 2. SUBSCRIPTION & REVENUE ---
print_header("FINANCIAL METRICS")
active_subs = Subscription.objects.filter(status='active').count()
total_revenue = Subscription.objects.filter(status='active').aggregate(total=Sum('amount'))['total'] or 0.0
conversion_rate = (active_subs / total_users * 100) if total_users else 0
avg_revenue = (total_revenue / active_subs) if active_subs else 0

print_stat("Total Revenue", f"${total_revenue:,.2f}")
print_stat("Active Subscriptions", active_subs)
print_stat("Conversion Rate", f"{conversion_rate:.1f}%")
print_stat("Avg Revenue / Sub", f"${avg_revenue:,.2f}")

# --- 3. PREDICTION STATS ---
print_header("PREDICTION ENGINE")
total_preds = Prediction.objects.filter(is_archived=False).count()
today_preds = Prediction.objects.filter(prediction_date__date=today, is_archived=False).count()
week_preds = Prediction.objects.filter(prediction_date__gte=week_ago, is_archived=False).count()
archived_preds = Prediction.objects.filter(is_archived=True).count()

print_stat("Total Active Preds", total_preds)
print_stat("Made Today", today_preds)
print_stat("Made This Week", week_preds)
print_stat("Archived (Old)", archived_preds)

# --- 4. DATABASE INVENTORY ---
print_header("DATABASE INVENTORY")
total_matches = Match.objects.count()
total_teams = Team.objects.count()
total_leagues = League.objects.count()

print_stat("Leagues Supported", total_leagues)
print_stat("Teams Indexed", total_teams)
print_stat("Historical Matches", total_matches)

print("\n" + "="*60 + "\n")
