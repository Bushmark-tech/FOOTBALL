"""
Diagnostic script to check Man City vs Fulham probability calculation.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("Diagnosing Man City vs Fulham Probability Calculation")
print("=" * 70)

# Load football data
from predictor.analytics import load_football_data, calculate_probabilities_original

print("\n1. Loading football data (dataset 1)...")
data = load_football_data(1)
print(f"   Data loaded: {len(data)} rows")
print(f"   Columns: {list(data.columns[:10])}...")

# Calculate probabilities
print("\n2. Calculating probabilities for Man City vs Fulham...")
probs = calculate_probabilities_original("Man City", "Fulham", data, version="v1")
print(f"   Result: {probs}")

# Show breakdown
print("\n3. Probability breakdown:")
if probs:
    print(f"   Home Win (Man City): {probs.get('Home Team Win', 0)}%")
    print(f"   Draw: {probs.get('Draw', 0)}%")
    print(f"   Away Win (Fulham): {probs.get('Away Team Win', 0)}%")
    print(f"   Total: {probs.get('Home Team Win', 0) + probs.get('Draw', 0) + probs.get('Away Team Win', 0)}%")
else:
    print("   No probabilities calculated!")

# Show decimal format (what template expects)
print("\n4. Decimal format (for template):")
if probs:
    home_decimal = probs.get('Home Team Win', 0) / 100.0
    draw_decimal = probs.get('Draw', 0) / 100.0
    away_decimal = probs.get('Away Team Win', 0) / 100.0
    print(f"   Home: {home_decimal:.4f}")
    print(f"   Draw: {draw_decimal:.4f}")
    print(f"   Away: {away_decimal:.4f}")

# Show normalized format
print("\n5. Normalized decimal format:")
if probs:
    home_decimal = probs.get('Home Team Win', 0) / 100.0
    draw_decimal = probs.get('Draw', 0) / 100.0
    away_decimal = probs.get('Away Team Win', 0) / 100.0
    total = home_decimal + draw_decimal + away_decimal
    if total > 0:
        home_norm = home_decimal / total
        draw_norm = draw_decimal / total
        away_norm = away_decimal / total
        print(f"   Home: {home_norm:.4f} ({home_norm * 100:.1f}%)")
        print(f"   Draw: {draw_norm:.4f} ({draw_norm * 100:.1f}%)")
        print(f"   Away: {away_norm:.4f} ({away_norm * 100:.1f}%)")
        print(f"   Total: {home_norm + draw_norm + away_norm:.4f}")

# Check for head-to-head data
print("\n6. Checking for head-to-head data...")
h2h = data[
    (data['HomeTeam'].astype(str).str.strip() == 'Man City') &
    (data['AwayTeam'].astype(str).str.strip() == 'Fulham')
]
print(f"   Found {len(h2h)} head-to-head matches")
if len(h2h) > 0:
    print("   H2H data exists - probabilities are based on historical matches")
    # Show last few matches
    print("\n7. Recent H2H matches:")
    for idx, row in h2h.tail(5).iterrows():
        date = row.get('Date', 'N/A')
        home_score = row.get('FTHG', 0)
        away_score = row.get('FTAG', 0)
        result = row.get('FTR', 'N/A')
        print(f"   {date}: Man City {home_score} - {away_score} Fulham (Result: {result})")
else:
    print("   No H2H data - probabilities are based on form/fallback")

print("\n" + "=" * 70)





