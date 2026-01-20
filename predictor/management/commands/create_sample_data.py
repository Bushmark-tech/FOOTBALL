from django.core.management.base import BaseCommand
from predictor.models import Prediction, Match, Team
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Create sample data for testing the dashboard'

    def handle(self, *args, **options):
        # Sample teams
        teams = [
            'Man City', 'Liverpool', 'Arsenal', 'Chelsea', 'Barcelona', 'Real Madrid',
            'Bayern Munich', 'Dortmund', 'PSG', 'Juventus', 'Milan', 'Inter',
            'Ath Madrid', 'Valencia', 'Sevilla', 'Napoli', 'Roma', 'Lazio'
        ]
        
        # Sample leagues
        leagues = ['Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Ligue 1']
        
        # Create sample teams if they don't exist
        for team_name in teams:
            Team.objects.get_or_create(
                name=team_name,
                defaults={
                    'league': random.choice(leagues),
                    'country': 'Various'
                }
            )
        
        # Create sample matches if they don't exist
        for i in range(20):
            home_team = random.choice(teams)
            away_team = random.choice([t for t in teams if t != home_team])
            match_date = datetime.now() - timedelta(days=random.randint(1, 30))
            
            Match.objects.get_or_create(
                home_team=home_team,
                away_team=away_team,
                match_date=match_date,
                defaults={
                    'home_score': random.randint(0, 3),
                    'away_score': random.randint(0, 3),
                    'league': random.choice(leagues),
                    'season': '2024/25'
                }
            )
        
        # Create sample predictions if they don't exist
        for i in range(15):
            home_team = random.choice(teams)
            away_team = random.choice([t for t in teams if t != home_team])
            prediction_date = datetime.now() - timedelta(days=random.randint(1, 7))
            
            home_score = random.randint(0, 3)
            away_score = random.randint(0, 3)
            confidence = random.uniform(0.6, 0.95)
            
            Prediction.objects.get_or_create(
                home_team=home_team,
                away_team=away_team,
                prediction_date=prediction_date,
                defaults={
                    'home_score': home_score,
                    'away_score': away_score,
                    'confidence': confidence
                }
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"[OK] Sample data created successfully!\n"
                f"  - Teams: {Team.objects.count()}\n"
                f"  - Matches: {Match.objects.count()}\n"
                f"  - Predictions: {Prediction.objects.count()}"
            )
        ) 