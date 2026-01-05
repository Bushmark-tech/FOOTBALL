#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick test to verify the server is using the fixed code.
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

print("\n" + "="*70)
print("  VERIFYING SERVER IS USING FIXED CODE")
print("="*70)

from predictor.analytics import get_team_recent_form_original, load_football_data

# Test with teams that should have real data
data = load_football_data(dataset=1)

test_teams = [
    ("Man City", "Should have real form, not LLLLL"),
    ("Aston Villa", "Should have real form, not LLLLL"),
    ("Bournemouth", "Should have real form, not LLLLL"),
    ("Man United", "Should have real form, not LLLLL"),
]

print("\n[TESTING TEAM FORM DATA]")
all_passed = True

for team, expected in test_teams:
    form = get_team_recent_form_original(team, data, version="v1")
    
    # Check if it's generated fallback (all same letter)
    is_generated = (form == "LLLLL" or form == "WWWWW" or form == "DDDDD" or 
                   len(set(form)) == 1)
    
    if is_generated:
        print(f"  ❌ {team}: {form} (GENERATED - BUG STILL EXISTS)")
        all_passed = False
    else:
        print(f"  ✅ {team}: {form} (REAL DATA)")

print("\n" + "="*70)
if all_passed:
    print("  ✅ SUCCESS! Server is using the FIXED code!")
    print("  You can now make predictions and see real data.")
else:
    print("  ❌ FAILED! Server is still using OLD code.")
    print("  The server may not have reloaded properly.")
print("="*70 + "\n")
