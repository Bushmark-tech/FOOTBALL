"""
Django management command to optimize database for production.
Run this after migrations to create indexes and optimize queries.
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Optimize database indexes and queries for production'

    def handle(self, *args, **options):
        self.stdout.write('Optimizing database for production...')
        
        with connection.cursor() as cursor:
            # Create indexes for frequently queried fields
            indexes = [
                # Prediction indexes
                "CREATE INDEX IF NOT EXISTS idx_prediction_date ON predictor_prediction(prediction_date DESC);",
                "CREATE INDEX IF NOT EXISTS idx_prediction_user ON predictor_prediction(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_prediction_teams ON predictor_prediction(home_team, away_team);",
                
                # Match indexes
                "CREATE INDEX IF NOT EXISTS idx_match_date ON predictor_match(match_date DESC);",
                "CREATE INDEX IF NOT EXISTS idx_match_league ON predictor_match(league_id);",
                
                # Team indexes
                "CREATE INDEX IF NOT EXISTS idx_team_name ON predictor_team(name);",
                "CREATE INDEX IF NOT EXISTS idx_team_league ON predictor_team(league_id);",
            ]
            
            for index_sql in indexes:
                try:
                    cursor.execute(index_sql)
                    self.stdout.write(self.style.SUCCESS(f'Created index: {index_sql[:50]}...'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Index may already exist: {e}'))
            
            # Analyze tables for query optimization
            cursor.execute("ANALYZE predictor_prediction;")
            cursor.execute("ANALYZE predictor_match;")
            cursor.execute("ANALYZE predictor_team;")
            cursor.execute("ANALYZE predictor_league;")
            
            self.stdout.write(self.style.SUCCESS('Database optimization complete!'))

