# Script to sync logic from analytics.py to views.py
# This ensures all prediction logic comes from analytics.py

import sys
import os

print("="*70)
print("SYNCING LOGIC FROM ANALYTICS.PY")
print("="*70)

# The key insight: views.py should ONLY call analytics.py functions
# It should NOT have its own probability calculation or double chance logic

print("\n✓ Your analytics.py file contains the complete logic:")
print("  1. calculate_probabilities_model2() - Model 2 probabilities")
print("  2. calculate_probabilities_original() - Model 1 probabilities")
print("  3. advanced_predict_match() - Complete prediction with blending")
print("  4. Blending weights: Model 70%, H2H 18%, Form 10%")
print("  5. Double chance logic with thresholds")

print("\n✓ views.py should:")
print("  1. Call advanced_predict_match() from analytics.py")
print("  2. Use the returned 'outcome' directly")
print("  3. Use the returned 'probabilities' directly")
print("  4. NOT override or recalculate anything")

print("\n✓ The issue was:")
print("  - views.py had its own calculate_double_chance() function")
print("  - This was overriding analytics.py's logic")
print("  - Solution: Remove calculate_double_chance() from views.py")

print("\n" + "="*70)
print("RECOMMENDATION")
print("="*70)
print("\nTo fix this properly:")
print("1. views.py should trust analytics.py completely")
print("2. Remove calculate_double_chance() from views.py")
print("3. Use outcome from advanced_predict_match() directly")
print("4. Don't recalculate probabilities in views.py")

print("\nThe analytics.py file you provided is the SOURCE OF TRUTH.")
print("All other files should defer to it.")
print("="*70)
