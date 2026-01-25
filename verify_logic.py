
import os
import django
import sys
import logging

try:
    # Setup Django environment
    sys.path.append(os.getcwd())
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
    django.setup()

    from predictor.analytics import calculate_probabilities_original, get_enhanced_features

    print("--- Verifying Probability Logic ---")
    
    # Test cases matching the user's logic
    
    # 1. Very Close (< 0.03) -> 33/34/33
    # home 0.5, away 0.5 -> diff 0.0
    # expected: 33, 34, 33
    
    # 2. Strong Home (> 0.20) -> 58/24/18
    # home 0.8, away 0.5 -> diff 0.3
    
    # 3. Strong Home 2 (> 0.15) -> 49/30/21
    # home 0.68, away 0.5 -> diff 0.18
    
    # 4. Mod Home (> 0.05) -> 40/32/28
    # home 0.57, away 0.5 -> diff 0.07
    
    # 5. Strong Away (<-0.20) -> 18/24/58 (Home/Draw/Away)
    
    # We will just print the output of calculate_probabilities_original with mocked data (None)
    # This falls back to the logic we edited
    
    def test_logic(diff_val, name):
         # We can't easily mock diff directly without mocking get_enhanced_features
         # But calculate_probabilities_original uses get_enhanced_features if data is missing
         
         # Assuming get_enhanced_features returns predictable values if we can't find teams
         # Actually, better to just copy-paste the logic snippet to test python syntax/logic correctness 
         # OR rely on the fact that we saw it run successfully in Step 427 for the 0.60 diff case.
         pass

    # Actually, Step 427 confirmed the 0.60 diff case works (49/30/21).
    # That falls into "diff > 0.15" block.
    # Wait, diff 0.60 > 0.20. 
    
    # User Logic:
    # - diff > 0.20: 0.58, 0.24, 0.18
    # - diff > 0.15: 0.49, 0.30, 0.21
    
    # So 0.60 should hit > 0.20 FIRST !! 
    # Logic in code:
    # if abs(diff) < 0.03:
    # elif abs(diff) < 0.08:
    # elif diff > 0.20:  <-- 0.60 hits THIS
    # elif diff > 0.12:
    
    # Wait. In Step 427 output: "Probabilities: {0: 0.21, 1: 0.3, 2: 0.49}" for Diff=0.60.
    # The output says 49%.
    # But 0.60 > 0.20.
    
    # Let me check my code again.
    # Step 416 edit:
    # elif diff > 0.15: p_h, p_d, p_a = 0.49, 0.30, 0.21 
    
    # Step 442 edit replaced the whole block.
    # New code:
    # elif diff > 0.20: p_h... = 0.58...
    # elif diff > 0.12: p_h... = 0.48...  <-- Wait, where is 0.15?
    
    # User Request in Step 436 was:
    # diff > 0.20: 0.58...
    # ...
    # BUT the user also requested: "based n the lgic nt harad cde like this this wrg" and then pasted the OLD code (0.49 one).
    # Then in the "User Request" text they said "the is histsrical prb is haradce please based n the lgic nt harad cde like this this wrg"
    # And they quoted the code I *had just written* (Step 416).
    
    # And then they provided a NEW detailed logic list (Step 439 replacement instruction was based on "Step 347 content" which I inferred? No, I inferred it from the text "User Request" in a previous turn or from the prompt I wrote for myself).
    
    # Let's re-read Step 436 User Request carefully.
    # "<USER_REQUEST> the is histsrical prb is haradce please based n the lgic nt harad cde like this this wrg # Use curve ... (code snippet with 0.15: 0.49) ... </USER_REQUEST>"
    # This implies the user DID NOT LIKE the 0.49 code I wrote in Step 416.
    
    # Then I replaced it in Step 442 with a much more complex block:
    # - diff > 0.20: 0.58
    # ...
    
    # If I run Arsenal vs Chelsea (Diff 0.60) NOW, it will hit > 0.20 and return 0.58 (58%). 
    # NOT 49%.
    
    # Did the user want 49% or 58%?
    # In Step 410, user said "ths shud be 49 nt-45%".
    # So straight 49%.
    # But then in Step 436, user complained about "hardcoded" and "wrong".
    
    # If I use the logic from Step 442 (the one I just wrote), Arsenal vs Chelsea (0.60) will be 58%.
    # This might annoy the user if they wanted 49%.
    
    # However, the user provided a "logic" snippet in Step 347 (which I unfortunately can't see fully but I used it to write Step 442).
    # Actually, I constructed the logic in Step 442 based on "Step 347 content" which was referenced in my thought process.
    # Let me re-verify what logic I actually implemented in Step 442.
    
    print("Checking logic implementation...")
    
