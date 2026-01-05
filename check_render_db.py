#!/usr/bin/env python
"""
Script to check database state and manually trigger seeding if needed.
Run this on Render via: python check_render_db.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.models import League, Team
from django.core.management import call_command
from django.core.cache import cache

def main():
    print("=" * 60)
    print("DATABASE DIAGNOSTIC CHECK")
    print("=" * 60)
    
    # Check league count
    league_count = League.objects.count()
    team_count = Team.objects.count()
    
    print(f"\n📊 Current Database State:")
    print(f"   Leagues: {league_count}")
    print(f"   Teams: {team_count}")
    
    if league_count == 0:
        print("\n⚠️  DATABASE IS EMPTY!")
        print("   Running seed_leagues command...")
        try:
            call_command('seed_leagues')
            print("   ✅ Seeding completed successfully")
            
            # Verify
            league_count = League.objects.count()
            team_count = Team.objects.count()
            print(f"\n📊 After Seeding:")
            print(f"   Leagues: {league_count}")
            print(f"   Teams: {team_count}")
        except Exception as e:
            print(f"   ❌ Seeding failed: {e}")
            return
    else:
        print("\n✅ Database has data")
        print("\nSample leagues:")
        for league in League.objects.all()[:5]:
            print(f"   - {league.name} ({league.category}): {league.teams.count()} teams")
    
    # Clear cache
    print("\n🔄 Clearing cache...")
    cache.clear()
    print("   ✅ Cache cleared")
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
