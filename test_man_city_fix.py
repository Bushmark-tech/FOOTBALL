#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test if Man City data is now found correctly.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.analytics import (
    load_team_mapping,
    load_football_data,
    find_team_in_data,
    get_team_recent_form_original
)

print("\n" + "="*70)
print("  TESTING MAN CITY DATA LOOKUP FIX")
print("="*70)

# Test 1: Check mapping
print("\n[TEST 1] Team Mapping")
mapping = load_team_mapping()
man_city_id = mapping.get("Man City")
print(f"  Man City ID: {man_city_id}")

# Test 2: Load data and check format
print("\n[TEST 2] Data Format")
data = load_football_data(dataset=1)
print(f"  Columns: {list(data.columns)[:5]}")
print(f"  Sample HomeTeam values: {data['HomeTeam'].head(5).tolist()}")
print(f"  Data type: {data['HomeTeam'].dtype}")

# Test 3: Find team in data
print("\n[TEST 3] Find Team in Data")
found = find_team_in_data("Man City", data, "HomeTeam")
print(f"  'Man City' found as: {found}")
print(f"  Type: {type(found)}")

# Test 4: Check if Man City has matches
print("\n[TEST 4] Man City Matches")
if found is not None:
    home_matches = (data['HomeTeam'] == found).sum()
    away_matches = (data['AwayTeam'] == found).sum()
    print(f"  Home matches: {home_matches}")
    print(f"  Away matches: {away_matches}")
    print(f"  Total matches: {home_matches + away_matches}")
else:
    print("  ✗ Team not found!")

# Test 5: Get team form
print("\n[TEST 5] Team Form")
form = get_team_recent_form_original("Man City", data, version="v1")
print(f"  Man City form: {form}")
print(f"  Form length: {len(form)}")

# Test with Liverpool too
print("\n[TEST 6] Liverpool (for comparison)")
liverpool_id = mapping.get("Liverpool")
print(f"  Liverpool ID: {liverpool_id}")
found_liverpool = find_team_in_data("Liverpool", data, "HomeTeam")
print(f"  'Liverpool' found as: {found_liverpool}")
if found_liverpool is not None:
    home_matches = (data['HomeTeam'] == found_liverpool).sum()
    away_matches = (data['AwayTeam'] == found_liverpool).sum()
    print(f"  Total matches: {home_matches + away_matches}")
form_liverpool = get_team_recent_form_original("Liverpool", data, version="v1")
print(f"  Liverpool form: {form_liverpool}")

print("\n" + "="*70)
print("  TEST COMPLETE")
print("="*70 + "\n")
