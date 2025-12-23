"""
Comprehensive tests for predictor models - testing all dimensions.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from predictor.models import Prediction, Match, League, Team
from datetime import date
import time


class PredictionModelTest(TestCase):
    """Test cases for Prediction model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_prediction_creation(self):
        """Test creating a prediction."""
        prediction = Prediction.objects.create(
            home_team='Man City',
            away_team='Liverpool',
            home_score=2,
            away_score=1,
            confidence=0.75,
            user=self.user,
            category='European Leagues',
            outcome='Home',
            prob_home=0.60,
            prob_draw=0.25,
            prob_away=0.15
        )
        
        self.assertEqual(prediction.home_team, 'Man City')
        self.assertEqual(prediction.away_team, 'Liverpool')
        self.assertEqual(prediction.confidence, 0.75)
        self.assertEqual(str(prediction), 'Man City vs Liverpool - 2:1')
    
    def test_prediction_without_user(self):
        """Test creating prediction without user."""
        prediction = Prediction.objects.create(
            home_team='Chelsea',
            away_team='Arsenal',
            home_score=1,
            away_score=1,
            confidence=0.50
        )
        
        self.assertIsNone(prediction.user)
        self.assertIsNone(prediction.outcome)  # outcome is None by default, not empty string
    
    def test_prediction_ordering(self):
        """Test that predictions are ordered by date descending."""
        pred1 = Prediction.objects.create(
            home_team='Team A',
            away_team='Team B',
            home_score=1,
            away_score=0,
            confidence=0.60
        )
        
        # Add small delay to ensure different timestamps
        time.sleep(0.01)
        
        pred2 = Prediction.objects.create(
            home_team='Team C',
            away_team='Team D',
            home_score=2,
            away_score=1,
            confidence=0.70
        )
        
        predictions = list(Prediction.objects.all())
        # Most recent should be first
        self.assertEqual(predictions[0], pred2)
    
    def test_prediction_all_fields(self):
        """Test all fields of Prediction model."""
        prediction = Prediction.objects.create(
            home_team='Arsenal',
            away_team='Chelsea',
            home_score=3,
            away_score=1,
            confidence=0.85,
            user=self.user,
            category='European Leagues',
            league='Premier League',
            outcome='Home',
            prob_home=0.65,
            prob_draw=0.20,
            prob_away=0.15,
            model_type='Model1',
            model1_prediction='Home Win',
            model2_prediction='Home Win',
            final_prediction='Home Win'
        )
        
        # Test all fields
        self.assertEqual(prediction.home_team, 'Arsenal')
        self.assertEqual(prediction.away_team, 'Chelsea')
        self.assertEqual(prediction.home_score, 3)
        self.assertEqual(prediction.away_score, 1)
        self.assertEqual(prediction.confidence, 0.85)
        self.assertEqual(prediction.user, self.user)
        self.assertEqual(prediction.category, 'European Leagues')
        self.assertEqual(prediction.league, 'Premier League')
        self.assertEqual(prediction.outcome, 'Home')
        self.assertEqual(prediction.prob_home, 0.65)
        self.assertEqual(prediction.prob_draw, 0.20)
        self.assertEqual(prediction.prob_away, 0.15)
        self.assertEqual(prediction.model_type, 'Model1')
        self.assertEqual(prediction.model1_prediction, 'Home Win')
        self.assertEqual(prediction.model2_prediction, 'Home Win')
        self.assertEqual(prediction.final_prediction, 'Home Win')
        self.assertIsNotNone(prediction.prediction_date)
    
    def test_prediction_default_values(self):
        """Test default values for Prediction model."""
        prediction = Prediction.objects.create(
            home_team='Team A',
            away_team='Team B',
            home_score=1,
            away_score=0,
            confidence=0.50
        )
        
        # Test defaults
        self.assertEqual(prediction.prob_home, 0.0)
        self.assertEqual(prediction.prob_draw, 0.0)
        self.assertEqual(prediction.prob_away, 0.0)
        self.assertIsNone(prediction.user)
        self.assertIsNone(prediction.category)
        self.assertIsNone(prediction.league)
        self.assertIsNone(prediction.outcome)
        # blank=True, null=True means these default to None, not empty string
        self.assertIsNone(prediction.model_type)
        self.assertIsNone(prediction.model1_prediction)
        self.assertIsNone(prediction.model2_prediction)
        self.assertIsNone(prediction.final_prediction)
    
    def test_prediction_field_max_length(self):
        """Test field max_length constraints."""
        # Test max_length for CharField fields
        long_name = 'A' * 101  # Exceeds max_length=100
        prediction = Prediction.objects.create(
            home_team='A' * 100,  # Exactly max_length
            away_team='B' * 100,
            home_score=1,
            away_score=0,
            confidence=0.50
        )
        
        # Should work with max_length
        self.assertEqual(len(prediction.home_team), 100)
        self.assertEqual(len(prediction.away_team), 100)
    
    def test_prediction_user_cascade_delete(self):
        """Test that predictions are deleted when user is deleted."""
        prediction = Prediction.objects.create(
            home_team='Team A',
            away_team='Team B',
            home_score=1,
            away_score=0,
            confidence=0.50,
            user=self.user
        )
        
        prediction_id = prediction.id
        self.user.delete()
        
        # Prediction should be deleted
        self.assertFalse(Prediction.objects.filter(id=prediction_id).exists())
    
    def test_prediction_string_representation(self):
        """Test string representation of Prediction."""
        prediction = Prediction.objects.create(
            home_team='Man United',
            away_team='Liverpool',
            home_score=2,
            away_score=1,
            confidence=0.75
        )
        
        self.assertEqual(str(prediction), 'Man United vs Liverpool - 2:1')
    
    def test_prediction_negative_scores(self):
        """Test that negative scores are allowed (edge case)."""
        prediction = Prediction.objects.create(
            home_team='Team A',
            away_team='Team B',
            home_score=-1,  # Negative score
            away_score=0,
            confidence=0.50
        )
        
        self.assertEqual(prediction.home_score, -1)
    
    def test_prediction_zero_confidence(self):
        """Test prediction with zero confidence."""
        prediction = Prediction.objects.create(
            home_team='Team A',
            away_team='Team B',
            home_score=1,
            away_score=0,
            confidence=0.0
        )
        
        self.assertEqual(prediction.confidence, 0.0)
    
    def test_prediction_high_confidence(self):
        """Test prediction with high confidence."""
        prediction = Prediction.objects.create(
            home_team='Team A',
            away_team='Team B',
            home_score=1,
            away_score=0,
            confidence=1.0
        )
        
        self.assertEqual(prediction.confidence, 1.0)


class MatchModelTest(TestCase):
    """Test cases for Match model."""
    
    def test_match_creation(self):
        """Test creating a match."""
        match = Match.objects.create(
            home_team='Barcelona',
            away_team='Real Madrid',
            home_score=3,
            away_score=2,
            match_date=date(2024, 1, 15),
            league='La Liga',
            season='2023-24'
        )
        
        self.assertEqual(match.home_team, 'Barcelona')
        self.assertEqual(match.away_team, 'Real Madrid')
        self.assertEqual(str(match), 'Barcelona vs Real Madrid (La Liga)')
    
    def test_match_without_scores(self):
        """Test creating match without scores."""
        match = Match.objects.create(
            home_team='Team A',
            away_team='Team B',
            match_date=date(2024, 1, 20),
            league='Premier League',
            season='2023-24'
        )
        
        self.assertIsNone(match.home_score)
        self.assertIsNone(match.away_score)
    
    def test_match_all_fields(self):
        """Test all fields of Match model."""
        match = Match.objects.create(
            home_team='Barcelona',
            away_team='Real Madrid',
            home_score=3,
            away_score=2,
            match_date=date(2024, 1, 15),
            league='La Liga',
            season='2023-24'
        )
        
        self.assertEqual(match.home_team, 'Barcelona')
        self.assertEqual(match.away_team, 'Real Madrid')
        self.assertEqual(match.home_score, 3)
        self.assertEqual(match.away_score, 2)
        self.assertEqual(match.match_date, date(2024, 1, 15))
        self.assertEqual(match.league, 'La Liga')
        self.assertEqual(match.season, '2023-24')
    
    def test_match_ordering(self):
        """Test that matches are ordered by date descending."""
        match1 = Match.objects.create(
            home_team='Team A',
            away_team='Team B',
            match_date=date(2024, 1, 10),
            league='League 1',
            season='2023-24'
        )
        
        match2 = Match.objects.create(
            home_team='Team C',
            away_team='Team D',
            match_date=date(2024, 1, 20),
            league='League 2',
            season='2023-24'
        )
        
        matches = list(Match.objects.all())
        # Most recent should be first
        self.assertEqual(matches[0], match2)
    
    def test_match_string_representation(self):
        """Test string representation of Match."""
        match = Match.objects.create(
            home_team='Arsenal',
            away_team='Chelsea',
            match_date=date(2024, 1, 15),
            league='Premier League',
            season='2023-24'
        )
        
        self.assertEqual(str(match), 'Arsenal vs Chelsea (Premier League)')
    
    def test_match_field_max_length(self):
        """Test field max_length constraints."""
        match = Match.objects.create(
            home_team='A' * 100,  # Exactly max_length
            away_team='B' * 100,
            match_date=date(2024, 1, 15),
            league='C' * 100,
            season='D' * 20  # Exactly max_length
        )
        
        self.assertEqual(len(match.home_team), 100)
        self.assertEqual(len(match.away_team), 100)
        self.assertEqual(len(match.league), 100)
        self.assertEqual(len(match.season), 20)
    
    def test_match_future_date(self):
        """Test match with future date."""
        future_date = date(2025, 12, 31)
        match = Match.objects.create(
            home_team='Team A',
            away_team='Team B',
            match_date=future_date,
            league='League',
            season='2024-25'
        )
        
        self.assertEqual(match.match_date, future_date)
    
    def test_match_past_date(self):
        """Test match with past date."""
        past_date = date(2020, 1, 1)
        match = Match.objects.create(
            home_team='Team A',
            away_team='Team B',
            match_date=past_date,
            league='League',
            season='2019-20'
        )
        
        self.assertEqual(match.match_date, past_date)


class LeagueModelTest(TestCase):
    """Test cases for League model."""
    
    def test_league_creation(self):
        """Test creating a league."""
        league = League.objects.create(
            name='Premier League',
            category='European Leagues',
            country='England'
        )
        
        self.assertEqual(league.name, 'Premier League')
        self.assertEqual(league.category, 'European Leagues')
        self.assertEqual(str(league), 'Premier League (European Leagues)')
    
    def test_league_unique_name(self):
        """Test that league names must be unique."""
        League.objects.create(
            name='Serie A',
            category='European Leagues'
        )
        
        # Try to create duplicate
        with self.assertRaises(IntegrityError):
            League.objects.create(
                name='Serie A',
                category='Others'
            )
    
    def test_league_all_fields(self):
        """Test all fields of League model."""
        league = League.objects.create(
            name='Premier League',
            category='European Leagues',
            country='England'
        )
        
        self.assertEqual(league.name, 'Premier League')
        self.assertEqual(league.category, 'European Leagues')
        self.assertEqual(league.country, 'England')
    
    def test_league_ordering(self):
        """Test that leagues are ordered by category then name."""
        league1 = League.objects.create(
            name='Bundesliga',
            category='European Leagues'
        )
        league2 = League.objects.create(
            name='Premier League',
            category='European Leagues'
        )
        league3 = League.objects.create(
            name='MLS',
            category='Others'
        )
        
        leagues = list(League.objects.all())
        # Should be ordered by category, then name
        self.assertEqual(leagues[0].category, 'European Leagues')
        self.assertEqual(leagues[-1].category, 'Others')
    
    def test_league_string_representation(self):
        """Test string representation of League."""
        league = League.objects.create(
            name='La Liga',
            category='European Leagues'
        )
        
        self.assertEqual(str(league), 'La Liga (European Leagues)')
    
    def test_league_without_country(self):
        """Test league without country (nullable field)."""
        league = League.objects.create(
            name='Serie A',
            category='European Leagues'
        )
        
        self.assertIsNone(league.country)
    
    def test_league_field_max_length(self):
        """Test field max_length constraints."""
        league = League.objects.create(
            name='A' * 100,  # Exactly max_length
            category='B' * 100,
            country='C' * 100
        )
        
        self.assertEqual(len(league.name), 100)
        self.assertEqual(len(league.category), 100)
        self.assertEqual(len(league.country), 100)


class TeamModelTest(TestCase):
    """Test cases for Team model."""
    
    def setUp(self):
        """Set up test data."""
        self.league = League.objects.create(
            name='Premier League',
            category='European Leagues'
        )
    
    def test_team_creation(self):
        """Test creating a team."""
        team = Team.objects.create(
            name='Arsenal',
            league=self.league,
            country='England'
        )
        
        self.assertEqual(team.name, 'Arsenal')
        self.assertEqual(team.league, self.league)
        self.assertEqual(str(team), 'Arsenal (Premier League)')
    
    def test_team_unique_name(self):
        """Test that team names must be unique."""
        Team.objects.create(
            name='Liverpool',
            league=self.league
        )
        
        # Try to create duplicate
        with self.assertRaises(IntegrityError):
            Team.objects.create(
                name='Liverpool',
                league=self.league
            )
    
    def test_team_league_relationship(self):
        """Test team-league relationship."""
        team = Team.objects.create(
            name='Chelsea',
            league=self.league
        )
        
        self.assertEqual(team.league.name, 'Premier League')
        self.assertIn(team, self.league.teams.all())
    
    def test_team_all_fields(self):
        """Test all fields of Team model."""
        team = Team.objects.create(
            name='Arsenal',
            league=self.league,
            country='England'
        )
        
        self.assertEqual(team.name, 'Arsenal')
        self.assertEqual(team.league, self.league)
        self.assertEqual(team.country, 'England')
    
    def test_team_ordering(self):
        """Test that teams are ordered by name."""
        team1 = Team.objects.create(name='Chelsea', league=self.league)
        team2 = Team.objects.create(name='Arsenal', league=self.league)
        team3 = Team.objects.create(name='Liverpool', league=self.league)
        
        teams = list(Team.objects.all())
        # Should be ordered alphabetically by name
        self.assertEqual(teams[0].name, 'Arsenal')
        self.assertEqual(teams[1].name, 'Chelsea')
        self.assertEqual(teams[2].name, 'Liverpool')
    
    def test_team_string_representation(self):
        """Test string representation of Team."""
        team = Team.objects.create(
            name='Manchester United',
            league=self.league
        )
        
        self.assertEqual(str(team), 'Manchester United (Premier League)')
    
    def test_team_without_country(self):
        """Test team without country (nullable field)."""
        team = Team.objects.create(
            name='Team A',
            league=self.league
        )
        
        self.assertIsNone(team.country)
    
    def test_team_league_cascade_delete(self):
        """Test that teams are deleted when league is deleted."""
        team = Team.objects.create(
            name='Test Team',
            league=self.league
        )
        
        team_id = team.id
        self.league.delete()
        
        # Team should be deleted due to CASCADE
        self.assertFalse(Team.objects.filter(id=team_id).exists())
    
    def test_team_related_name(self):
        """Test the related_name 'teams' on League model."""
        team1 = Team.objects.create(name='Team 1', league=self.league)
        team2 = Team.objects.create(name='Team 2', league=self.league)
        
        # Access teams through related_name
        teams = self.league.teams.all()
        self.assertEqual(teams.count(), 2)
        self.assertIn(team1, teams)
        self.assertIn(team2, teams)
    
    def test_team_field_max_length(self):
        """Test field max_length constraints."""
        team = Team.objects.create(
            name='A' * 100,  # Exactly max_length
            league=self.league,
            country='B' * 100
        )
        
        self.assertEqual(len(team.name), 100)
        self.assertEqual(len(team.country), 100)
    
    def test_team_unique_name_across_leagues(self):
        """Test that team names must be unique across all leagues."""
        league2 = League.objects.create(
            name='La Liga',
            category='European Leagues'
        )
        
        team1 = Team.objects.create(name='Real Madrid', league=self.league)
        
        # Should fail - name has unique=True constraint
        with self.assertRaises(IntegrityError):
            Team.objects.create(name='Real Madrid', league=league2)

