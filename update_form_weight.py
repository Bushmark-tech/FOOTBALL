import re

# Read the file
with open('predictor/analytics.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the form blending section with intelligent weighting
old_form_blend = r'''             # Blend with Form \(Current blend 90%, Form 10%\)
             # Final weights: Model ~70%, H2H ~18%, Form ~10%
             if form_probs:
                   for k in final_probs:
                        final_probs\[k\] = final_probs\.get\(k, 0\.33\) \* 0\.90 \+ form_probs\.get\(k, 0\.33\) \* 0\.10'''

new_form_blend = '''             # INTELLIGENT FORM BLENDING
             # Adjust form weight based on how different the teams' forms are
             # If one team has significantly better form, give form MORE weight
             if form_probs:
                   # Calculate form difference to determine weight
                   # form_probs format: {0: away_prob, 1: draw_prob, 2: home_prob}
                   form_home = form_probs.get(2, 0.33)
                   form_away = form_probs.get(0, 0.33)
                   form_diff = abs(form_home - form_away)
                   
                   # Dynamic form weight based on form difference:
                   # - Small difference (<0.10): 10% form weight (original)
                   # - Medium difference (0.10-0.20): 15% form weight
                   # - Large difference (0.20-0.30): 25% form weight
                   # - Huge difference (>0.30): 35% form weight (exceptional form like WWWWW)
                   if form_diff > 0.30:
                       form_weight = 0.35  # Exceptional form difference
                       logger.info(f"Exceptional form difference detected ({form_diff:.2f}), using 35% form weight")
                   elif form_diff > 0.20:
                       form_weight = 0.25  # Large form difference
                       logger.info(f"Large form difference detected ({form_diff:.2f}), using 25% form weight")
                   elif form_diff > 0.10:
                       form_weight = 0.15  # Medium form difference
                       logger.info(f"Medium form difference detected ({form_diff:.2f}), using 15% form weight")
                   else:
                       form_weight = 0.10  # Small difference, use default
                   
                   # Blend: Current * (1 - form_weight) + Form * form_weight
                   for k in final_probs:
                        final_probs[k] = final_probs.get(k, 0.33) * (1 - form_weight) + form_probs.get(k, 0.33) * form_weight
                   
                   # Final weights with dynamic form:
                   # Base: Model ~70%, H2H ~18%, Form ~10-35% (dynamic)
                   logger.info(f"Final blend weights: Model ~{70*(1-form_weight):.0f}%, H2H ~{18*(1-form_weight):.0f}%, Form ~{form_weight*100:.0f}%")'''

# Replace
content_new = re.sub(old_form_blend, new_form_blend, content, flags=re.MULTILINE)

if content_new != content:
    with open('predictor/analytics.py', 'w', encoding='utf-8') as f:
        f.write(content_new)
    print("✓ Successfully updated form blending with intelligent weighting!")
    print("\nNew behavior:")
    print("  - Small form diff (<10%): 10% form weight (default)")
    print("  - Medium form diff (10-20%): 15% form weight")
    print("  - Large form diff (20-30%): 25% form weight")
    print("  - Exceptional form diff (>30%): 35% form weight")
    print("\nThis will give Arsenal's perfect form (WWWWW) much more influence!")
else:
    print("✗ Pattern not found - analytics.py may have been modified")
