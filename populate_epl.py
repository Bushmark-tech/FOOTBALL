#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Populate English Premier League and Europe League teams.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.models import League, Team

def populate():
    print("\n" + "="*70)
    print("  POPULATING EPL and EUROPE LEAGUE")
    print("="*70)

    # 1. English Premier League
    epl_league, created = League.objects.get_or_create(
        name="English Premier League",
        defaults={'country': 'England', 'category': 'Professional'}
    )
    if created:
        print(f"✓ Created league: English Premier League")
    else:
        print(f"- League exists: English Premier League")

    epl_teams = [
        "Nott'm Forest", "Brentford", "Liverpool", "Leeds", "Fulham",
        "Tottenham", "Burnley", "Crystal Palace", "West Ham", "Bournemouth",
        "Newcastle", "Man United", "Arsenal", "Brighton", "Everton",
        "Aston Villa", "Man City", "Chelsea", "Wolves"
    ]

    for team_name in epl_teams:
        team, created = Team.objects.get_or_create(
            name=team_name,
            defaults={'league': epl_league, 'country': 'England'}
        )
        if created:
            print(f"  ✓ Created team: {team_name}")
        else:
            print(f"  - Team exists: {team_name}")

    # 2. Europe League (Requested for Sunderland)
    europe_league, created = League.objects.get_or_create(
        name="Europe League",
        defaults={'country': 'Europe', 'category': 'International'}
    )
    if created:
        print(f"✓ Created league: Europe League")
    else:
        print(f"- League exists: Europe League")

    sunderland_team, created = Team.objects.get_or_create(
        name="Sunderland",
        defaults={'league': europe_league, 'country': 'England'}
    )
    if created:
        print(f"  ✓ Created team: Sunderland")
    else:
        print(f"  - Team exists: Sunderland")

    print("\n" + "="*70)
    print("  SUMMARY")
    print("="*70)
    print(f"Total teams in database: {Team.objects.count()}")
    print("="*70 + "\n")

if __name__ == "__main__":
    populate()
