#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test with detailed logging to see what's happening.
"""

import os
import sys
import django
import logging

# Set up logging to see INFO messages
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.analytics import get_team_recent_form_original, load_football_data

print("\n" + "="*70)
print("  DETAILED DEBUG TEST")
print("="*70)

data = load_football_data(dataset=1)

print("\n[Testing Man City]")
print("-" * 70)
form = get_team_recent_form_original("Man City", data, version="v1")
print(f"\nRESULT: Man City form = {form}")

print("\n[Testing Fulham]")
print("-" * 70)
form = get_team_recent_form_original("Fulham", data, version="v1")
print(f"\nRESULT: Fulham form = {form}")

print("\n" + "="*70 + "\n")
