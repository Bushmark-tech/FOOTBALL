# Fix the calculate_double_chance function
import sys

# Read the file
with open('c:/Users/user/Desktop/Ftball_main/FOOTBALL/predictor/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the problematic section
old_code = """    # Logic to decide between single outcome and double chance:
    # 1. If the best single outcome is confident (>= 40%), use it directly
    if best_single_prob >= CLEAR_WIN_THRESHOLD:
        return best_single_name
    
    # 2. Check if top two outcomes are very close (within UNCERTAINTY_THRESHOLD)
    prob_difference = best_single_prob - second_best_single_prob
    
    # 3. Only use double chance if ALL of these conditions are met:
    #    a) The top two outcomes are VERY close (< 3% difference), AND
    #    b) The double chance is significantly better (>= 15% advantage), AND
    #    c) No single outcome has >= 40% probability (no clear favorite)
    if (prob_difference < UNCERTAINTY_THRESHOLD and 
        (best_double_prob - best_single_prob) >= DOUBLE_CHANCE_MIN_ADVANTAGE and
        best_single_prob < 0.40):
        return best_double_name
    
    # 4. Default to the best single outcome (most common case)
    return best_single_name"""

new_code = """    # Logic to decide between single outcome and double chance:
    # Match the logic from analytics.py for consistency
    prob_difference = best_single_prob - second_best_single_prob
    
    # Use double chance if confidence is low (< 45%) OR outcomes are close (< 8%)
    if best_single_prob < CLEAR_WIN_THRESHOLD or prob_difference < UNCERTAINTY_THRESHOLD:
        return best_double_name
    
    # Default to the best single outcome
    return best_single_name"""

if old_code in content:
    content = content.replace(old_code, new_code)
    print("✓ Found and replaced the code")
else:
    print("✗ Could not find the exact code to replace")
    print("Searching for partial match...")
    if "Logic to decide between single outcome" in content:
        print("✓ Found the section, but content doesn't match exactly")
    else:
        print("✗ Section not found at all")
    sys.exit(1)

# Write back
with open('c:/Users/user/Desktop/Ftball_main/FOOTBALL/predictor/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ File updated successfully!")
