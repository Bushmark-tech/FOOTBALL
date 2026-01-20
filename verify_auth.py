import os
import django
from django.contrib.auth import authenticate

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

u1 = authenticate(username='james0082', password='admin123')
u2 = authenticate(username='superadmin', password='admin123')

print(f"James: {u1}")
print(f"SuperAdmin: {u2}")
