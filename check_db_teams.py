
import os
import sys
import django

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.models import League, Team

def check_teams():
    print("Checking Database Teams...")
    leagues = League.objects.filter(category='Others')
    print(f"Number of 'Others' leagues: {leagues.count()}")
    for l in leagues:
        print(f"  - {l.name}")
        
    yb = Team.objects.filter(name='Young Boys').first()
    if yb:
        print(f"Found Young Boys in league: {yb.league.name} (Category: {yb.league.category})")
    else:
        print("Young Boys NOT found in database!")
        
    basel = Team.objects.filter(name='Basel').first()
    if basel:
        print(f"Found Basel in league: {basel.league.name} (Category: {basel.league.category})")
    else:
        print("Basel NOT found in database!")

if __name__ == "__main__":
    check_teams()
