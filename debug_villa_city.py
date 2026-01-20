#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug why Aston Villa vs Man City shows no data.
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

print("\n" + "="*70)
print("  DEBUGGING ASTON VILLA VS MAN CITY")
print("="*70)

from predictor.analytics import (
    load_team_mapping,
    load_football_data,
    find_team_in_data,
    get_team_recent_form_original,
    calculate_probabilities_original
)

# Load mapping and data
mapping = load_team_mapping()
data = load_football_data(dataset=1)

print(f"\n[1] Team IDs")
print(f"  Aston Villa: {mapping.get('Aston Villa')}")
print(f"  Man City: {mapping.get('Man City')}")

print(f"\n[2] Find teams in data")
villa_found = find_team_in_data("Aston Villa", data, "HomeTeam")
city_found = find_team_in_data("Man City", data, "HomeTeam")
print(f"  Aston Villa found as: {villa_found} (type: {type(villa_found)})")
print(f"  Man City found as: {city_found} (type: {type(city_found)})")

print(f"\n[3] Check matches in data")
if villa_found is not None:
    villa_matches = ((data['HomeTeam'] == villa_found) | (data['AwayTeam'] == villa_found)).sum()
    print(f"  Aston Villa matches: {villa_matches}")
else:
    print(f"  Aston Villa: NOT FOUND")

if city_found is not None:
    city_matches = ((data['HomeTeam'] == city_found) | (data['AwayTeam'] == city_found)).sum()
    print(f"  Man City matches: {city_matches}")
else:
    print(f"  Man City: NOT FOUND")

print(f"\n[4] Team Form")
villa_form = get_team_recent_form_original("Aston Villa", data, version="v1")
city_form = get_team_recent_form_original("Man City", data, version="v1")
print(f"  Aston Villa form: {villa_form}")
print(f"  Man City form: {city_form}")

print(f"\n[5] H2H Probabilities")
h2h_probs = calculate_probabilities_original("Aston Villa", "Man City", data, version="v1")
if h2h_probs:
    print(f"  Home: {h2h_probs.get('Home Team Win', 0):.1f}%")
    print(f"  Draw: {h2h_probs.get('Draw', 0):.1f}%")
    print(f"  Away: {h2h_probs.get('Away Team Win', 0):.1f}%")
else:
    print(f"  No H2H probabilities returned")

print("\n" + "="*70 + "\n")
