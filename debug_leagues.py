
import os
import django
import sys
import codecs

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.models import Prediction, BillingUsage

def debug_leagues_user():
    # Force UTF-8 output
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    
    print("Debugging User Predictions:")
    
    predictions = Prediction.objects.all().order_by('-prediction_date')
    
    for p in predictions:
        u_str = p.user.username if p.user else "None"
        l_str = str(p.league).encode('ascii', 'ignore').decode('ascii') # Strip weird chars
        print(f"ID:{p.id} | {p.home_team} vs {p.away_team} | League: '{l_str}' | User: {u_str}")
        
    print("\nCheck BillingUsage:")
    for b in BillingUsage.objects.all():
        print(f"Billing: {b.id} User: {b.user} | Leagues: {b.unique_leagues_count}")
        b.update_statistics()
        print(f"  -> Recalculated: {b.unique_leagues_count}")

if __name__ == '__main__':
    debug_leagues_user()
