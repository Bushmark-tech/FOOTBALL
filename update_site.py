
import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from django.contrib.sites.models import Site
from django.conf import settings

def update_site_domain():
    print("Checking Site configuration...")
    
    # Get the current site (ID=1 is standard for valid django-allauth setups)
    try:
        site = Site.objects.get(pk=settings.SITE_ID)
    except Site.DoesNotExist:
        print(f"Site with ID {settings.SITE_ID} not found. Creating it.")
        site = Site(pk=settings.SITE_ID)
    
    print(f"Current Site in DB: {site.domain} ({site.name})")
    
    # The domain we want (Primary production domain)
    # Adjust this if you want 'football-o48u.onrender.com' instead
    target_domain = 'leon-football.com' 
    target_name = 'Football Predictor'
    
    if site.domain != target_domain:
        print(f"Updating Site to: {target_domain}")
        site.domain = target_domain
        site.name = target_name
        site.save()
        print("Success: Site updated.")
    else:
        print("Site is already configured correctly.")

if __name__ == "__main__":
    update_site_domain()
