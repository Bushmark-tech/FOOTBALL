#!/usr/bin/env python3
"""Fix broken Django template variables in result.html"""

import re

# Read the file
with open('templates/predictor/result.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all broken template variables that are split across lines
# Pattern: {{ followed by newline and whitespace, then variable name }}
fixes = [
    # Fix home_team
    (r'{{\s*\n\s*home_team\s*}}', '{{ home_team }}'),
    # Fix away_team  
    (r'{{\s*\n\s*away_team\s*}}', '{{ away_team }}'),
    # Fix prediction_stats.total_count
    (r'{{\s*\n\s*prediction_stats\.total_count\s*}}', '{{ prediction_stats.total_count }}'),
    # Fix prediction_stats.home_count
    (r'{{\s*prediction_stats\.home_count\s*\n\s*}}', '{{ prediction_stats.home_count }}'),
    # Fix prediction_stats.home_percentage
    (r'{{\s*\n\s*prediction_stats\.home_percentage', '{{ prediction_stats.home_percentage'),
    # Fix prediction_stats.draw_count
    (r'{{\s*prediction_stats\.draw_count\s*\n\s*}}', '{{ prediction_stats.draw_count }}'),
    # Fix prediction_stats.draw_percentage
    (r'{{\s*\n\s*prediction_stats\.draw_percentage', '{{ prediction_stats.draw_percentage'),
    # Fix prediction_stats.away_count
    (r'{{\s*prediction_stats\.away_count\s*\n\s*}}', '{{ prediction_stats.away_count }}'),
    # Fix prediction_stats.away_percentage
    (r'{{\s*\n\s*prediction_stats\.away_percentage', '{{ prediction_stats.away_percentage'),
]

# Apply all fixes
for pattern, replacement in fixes:
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

# Write back
with open('templates/predictor/result.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed all broken template variables!")
print("🔄 Please refresh your browser to see the changes.")
