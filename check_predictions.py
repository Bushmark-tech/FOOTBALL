#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.models import Prediction

preds = Prediction.objects.filter(
    home_team__iexact='Chelsea',
    away_team__iexact='Crystal Palace'
).order_by('-prediction_date')

print(f'\nFound {preds.count()} predictions for Chelsea vs Crystal Palace:\n')
for p in preds[:10]:
    print(f'ID: {p.id}')
    print(f'Date: {p.prediction_date}')
    print(f'Probabilities: Home={p.prob_home*100:.1f}%, Draw={p.prob_draw*100:.1f}%, Away={p.prob_away*100:.1f}%')
    print(f'Outcome: {p.outcome}')
    print('-' * 60)

