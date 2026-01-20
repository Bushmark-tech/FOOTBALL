import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.views import calculate_double_chance

def test_case(name, h, d, a):
    print(f"Testing {name}: H={h}, D={d}, A={a}")
    result = calculate_double_chance(h, d, a)
    print(f"-> Result: {result}")
    return result

print("--- DEBUGGING DOUBLE CHANCE ---")
test_case("1X Case", 0.40, 0.35, 0.25)
test_case("Home Strong", 0.70, 0.15, 0.15)
test_case("Close Call", 0.45, 0.30, 0.25) 
test_case("Equal", 0.33, 0.34, 0.33)
test_case("Edge Draw", 0.05, 0.90, 0.05)
