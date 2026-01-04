"""
Management command to set up the Site object for django-allauth.
"""
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Sets up the Site object for django-allauth'

    def handle(self, *args, **options):
        site, created = Site.objects.get_or_create(
            id=1,
            defaults={
                'domain': '127.0.0.1:8000',
                'name': 'Football Predictor Pro'
            }
        )
        
        if not created:
            site.domain = '127.0.0.1:8000'
            site.name = 'Football Predictor Pro'
            site.save()
            self.stdout.write(self.style.SUCCESS(f'Site updated: {site.domain}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Site created: {site.domain}'))

