# Smart Prediction Logic with Double Chance

## Overview

This document describes the enhanced prediction logic that combines model predictions with historical probabilities to provide more accurate predictions, including Double Chance options.

## Prediction Rules

### Rule 1: Model and History Agree (High Confidence)
**Condition:** Model prediction matches the highest historical probability AND that probability > 40%

**Action:** Use the model prediction with high confidence

**Examples:**
- Model: Home, Historical: Home 50%, Draw 30%, Away 20% → **Prediction: Home Win** ✅
- Model: Draw, Historical: Home 25%, Draw 50%, Away 25% → **Prediction: Draw** ✅
- Model: Away, Historical: Home 20%, Draw 30%, Away 50% → **Prediction: Away Win** ✅

### Rule 2: Model Says Home/Away BUT History Shows Draw Dominance (Double Chance)
**Condition:** Model predicts Home/Away BUT Draw probability > 50%

**Action:** Predict Double Chance (Draw or Model's choice)

**Examples:**
- Model: Home, Historical: Home 20%, Draw 60%, Away 20% → **Prediction: Home or Draw (1X)** 🔄
- Model: Away, Historical: Home 20%, Draw 60%, Away 20% → **Prediction: Away or Draw (X2)** 🔄

### Rule 3: Model and History Disagree (Uncertainty - Double Chance)
**Condition:** Model prediction does NOT match highest historical probability AND no clear winner (all < 45%)

**Action:** Predict Double Chance covering the two most likely outcomes

**Examples:**
- Model: Home, Historical: Home 20%, Draw 40%, Away 40% → **Prediction: Draw or Away (X2)** 🔄
- Model: Away, Historical: Home 40%, Draw 40%, Away 20% → **Prediction: Home or Draw (1X)** 🔄

### Rule 4: Clear Historical Winner, Model Disagrees (Low Confidence)
**Condition:** Historical probability has clear winner (> 50%) BUT model predicts differently

**Action:** Use historical probability with medium confidence

**Examples:**
- Model: Home, Historical: Home 15%, Draw 20%, Away 65% → **Prediction: Away Win** (with note: Model disagreed)
- Model: Draw, Historical: Home 60%, Draw 20%, Away 20% → **Prediction: Home Win** (with note: Model disagreed)

### Rule 5: Very Close Probabilities (Triple Chance)
**Condition:** All three probabilities are very close (within 10% of each other)

**Action:** Predict the outcome with highest combined score (model + historical)

**Examples:**
- Model: Home, Historical: Home 35%, Draw 33%, Away 32% → **Prediction: Home Win** (Low confidence)
- Model: Draw, Historical: Home 34%, Draw 33%, Away 33% → **Prediction: Draw** (Very low confidence)

## Double Chance Notation

- **1X**: Home Win or Draw
- **X2**: Draw or Away Win
- **12**: Home Win or Away Win (rare, used when draw is very unlikely)

## Implementation Priority

1. Check if model and history agree (Rule 1) - Highest confidence
2. Check for draw dominance (Rule 2) - Double chance
3. Check for disagreement with uncertainty (Rule 3) - Double chance
4. Check for clear historical winner (Rule 4) - Medium confidence
5. Handle very close probabilities (Rule 5) - Low confidence

## Confidence Levels

- **High (>70%)**: Model and history agree, clear winner
- **Medium (50-70%)**: Some agreement, or clear historical pattern
- **Low (30-50%)**: Disagreement but manageable
- **Very Low (<30%)**: High uncertainty, close probabilities

