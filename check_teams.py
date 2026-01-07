"""
Script to check which teams have historical match data
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.models import League, Team
import pandas as pd

print("=" * 70)
print("TEAMS WITH HISTORICAL DATA IN DATABASE")
print("=" * 70)

# Get all leagues and teams from database
leagues = League.objects.all().prefetch_related('teams')

print(f"\nTotal Leagues in Database: {leagues.count()}")
print(f"Total Teams in Database: {Team.objects.count()}")

print("\n" + "=" * 70)
print("TEAMS BY LEAGUE (These are available for predictions)")
print("=" * 70)

for league in leagues:
    teams = league.teams.all()
    if teams.exists():
        print(f"\n📊 {league.name} ({league.category})")
        print(f"   Teams: {teams.count()}")
        team_names = sorted([team.name for team in teams])
        for i, team in enumerate(team_names, 1):
            print(f"   {i}. {team}")

print("\n" + "=" * 70)
print("RECOMMENDATION")
print("=" * 70)
print("\n✅ Use teams from the lists above for predictions")
print("✅ These teams are in your database and will show proper form data")
print("✅ For best results, try Swiss League teams (Basel, Lugano, Luzern, etc.)")
print("\n⚠️  Teams NOT in the database (like Liverpool, Arsenal) will use fallback data")
print("=" * 70)
