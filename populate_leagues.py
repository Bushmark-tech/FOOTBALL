#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Populate leagues and teams for Switzerland, Denmark, Austria, Mexico, Russia, and Romania.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.models import League, Team

# League and team data
leagues_data = {
    'Switzerland': {
        'country': 'Switzerland',
        'teams': [
            ('Sion', 94),
            ('St. Gallen', 98),
            ('Thun', 102),
            ('Zurich', 128),
            ('Young Boys', 125),
            ('Servette', 92),
            ('Basel', 16),
            ('Luzern', 61),
            ('Lugano', 60),
            ('Lausanne', 57),
            ('Grasshoppers', 45),
            ('Winterthur', 121),
        ]
    },
    'Denmark': {
        'country': 'Denmark',
        'teams': [
            ('Midtjylland', 66),
            ('Odense', 72),
            ('Sonderjyske', 96),
            ('Brondby', 17),
            ('FC Copenhagen', 34),
            ('Silkeborg', 93),
            ('Randers FC', 82),
            ('Aarhus', 3),
            ('Nordsjaelland', 71),
            ('Vejle', 117),
            ('Viborg', 119),
            ('Fredericia', 42),
        ]
    },
    'Austria': {
        'country': 'Austria',
        'teams': [
            ('SK Rapid', 86),
            ('Tirol', 104),
            ('LASK', 56),
            ('Sturm Graz', 100),
            ('Austria Vienna', 13),
            ('Altach', 8),
            ('Hartberg', 48),
            ('Salzburg', 88),
            ('Wolfsberger AC', 122),
            ('Ried', 83),
            ('BW Linz', 14),
            ('Grazer AK', 46),
        ]
    },
    'Mexico': {
        'country': 'Mexico',
        'teams': [
            ('Atlas', 12),
            ('Atl. San Luis', 11),
            ('Puebla', 79),
            ('Pachuca', 75),
            ('Necaxa', 70),
            ('Tigres UANL', 103),
            ('Toluca', 105),
            ('Club America', 22),
            ('Santos Laguna', 89),
            ('Club Tijuana', 24),
            ('UNAM Pumas', 110),
            ('Club Leon', 23),
            ('Cruz Azul', 26),
            ('Guadalajara Chivas', 47),
            ('Queretaro', 80),
            ('Monterrey', 69),
            ('Juarez', 52),
            ('Mazatlan FC', 64),
        ]
    },
    'Russia': {
        'country': 'Russia',
        'teams': [
            ('FK Rostov', 39),
            ('Spartak Moscow', 97),
            ('Zenit', 127),
            ('Krylya Sovetov', 55),
            ('Akhmat Grozny', 6),
            ('Lokomotiv Moscow', 59),
            ('CSKA Moscow', 19),
            ('Dynamo Moscow', 30),
            ('Sochi', 95),
            ('Krasnodar', 54),
            ('Orenburg', 73),
            ('Rubin Kazan', 85),
            ('Pari NN', 76),
            ('Baltika', 15),
            ('Akron Togliatti', 7),
            ('Dynamo Makhachkala', 29),
        ]
    },
    'Romania': {
        'country': 'Romania',
        'teams': [
            ('CFR Cluj', 18),
            ('FCSB', 38),
            ('FC Hermannstadt', 35),
            ('FC Botosani', 33),
            ('Din. Bucuresti', 28),
            ('FC Arges', 32),
            ('UTA Arad', 111),
            ('Univ. Craiova', 114),
            ('FC Rapid Bucuresti', 36),
            ('Farul Constanta', 41),
            ('U. Cluj', 109),
            ('Petrolul', 77),
            ('Otelul', 74),
            ('Csikszereda M. Ciuc', 27),
            ('Unirea Slobozia', 113),
            ('Metaloglobus Bucharest', 65),
        ]
    },
}

def populate_leagues_and_teams():
    """Populate leagues and teams in the database."""
    
    print("\n" + "="*70)
    print("  POPULATING LEAGUES AND TEAMS")
    print("="*70)
    
    total_leagues_created = 0
    total_leagues_updated = 0
    total_teams_created = 0
    total_teams_updated = 0
    
    for league_name, league_info in leagues_data.items():
        print(f"\n[{league_name}]")
        
        # Create or update league
        league, created = League.objects.get_or_create(
            name=league_name,
            defaults={'country': league_info['country']}
        )
        
        if created:
            total_leagues_created += 1
            print(f"  ✓ Created league: {league_name}")
        else:
            # Update country if it changed
            if league.country != league_info['country']:
                league.country = league_info['country']
                league.save()
                total_leagues_updated += 1
                print(f"  ↻ Updated league: {league_name}")
            else:
                print(f"  - League exists: {league_name}")
        
        # Create or update teams
        for team_name, team_code in league_info['teams']:
            team, created = Team.objects.get_or_create(
                name=team_name,
                defaults={
                    'league': league,
                }
            )
            
            if created:
                total_teams_created += 1
                print(f"    ✓ Created team: {team_name}")
            else:
                # Update if league changed
                if team.league != league:
                    team.league = league
                    team.save()
                    total_teams_updated += 1
                    print(f"    ↻ Updated team: {team_name}")
                else:
                    print(f"    - Team exists: {team_name}")
    
    # Summary
    print("\n" + "="*70)
    print("  SUMMARY")
    print("="*70)
    print(f"Leagues created: {total_leagues_created}")
    print(f"Leagues updated: {total_leagues_updated}")
    print(f"Teams created: {total_teams_created}")
    print(f"Teams updated: {total_teams_updated}")
    print(f"\nTotal leagues in database: {League.objects.count()}")
    print(f"Total teams in database: {Team.objects.count()}")
    print("="*70 + "\n")

if __name__ == "__main__":
    populate_leagues_and_teams()
