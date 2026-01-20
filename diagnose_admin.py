import os
import django
import sys
import traceback
from datetime import timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings_production')
try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

from django.utils import timezone
from django.db.models import Sum, Count
from django.contrib.auth import get_user_model
from django.conf import settings
from predictor.models import Prediction, BillingUsage, Subscription, Match, Team, League

User = get_user_model()

print("\n🔍 DIAGNOSING ADMIN DASHBOARD QUERIES...\n")

try:
    # Simulate queries from admin_dashboard view
    print("1. Checking Timezone...")
    today = timezone.now().date()
    week_ago = timezone.now() - timedelta(days=7)
    month_ago = timezone.now() - timedelta(days=30)
    print(f"   Date: {today}")

    print("2. Checking User Stats...")
    total_users = User.objects.count()
    active_users = User.objects.filter(
        prediction__prediction_date__gte=week_ago
    ).distinct().count()
    print(f"   Total Users: {total_users}, Active: {active_users}")

    print("3. Checking Social Account...")
    try:
        from allauth.socialaccount.models import SocialAccount
        google_users_count = SocialAccount.objects.filter(provider='google').count()
        print(f"   Google Users: {google_users_count}")
    except Exception as e:
        print(f"   ⚠️ AllAuth not installed/configured (Expected if not used): {e}")

    print("4. Checking Prediction Stats...")
    total_predictions = Prediction.objects.filter(is_archived=False).count()
    print(f"   Total Predictions: {total_predictions}")

    print("5. Checking Subscriptions...")
    active_subscriptions = Subscription.objects.filter(status='active').count()
    total_revenue = Subscription.objects.filter(
        status='active'
    ).aggregate(total=Sum('amount'))['total'] or 0
    print(f"   Active Subs: {active_subscriptions}, Revenue: {total_revenue}")

    print("6. Checking Database Objects...")
    total_matches = Match.objects.count()
    total_teams = Team.objects.count()
    total_leagues = League.objects.count()
    print(f"   Matches: {total_matches}, Teams: {total_teams}")

    print("\n✅ ALL QUERIES PASSED SUCCESSFULY.")
    print("The 500 error is likely in the TEMPLATE rendering, not the database logic.")

except Exception as e:
    print("\n❌ CRITICAL ERROR FOUND IN LOGIC:")
    traceback.print_exc()
