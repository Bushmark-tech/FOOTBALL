from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Prediction(models.Model):
    """Model for storing football match predictions.
    
    Optimized for high-traffic scenarios with:
    - Database indexes on frequently queried fields
    - Auto-archiving of old predictions
    - Efficient bulk operations
    """
    home_team = models.CharField(max_length=100, db_index=True)
    away_team = models.CharField(max_length=100, db_index=True)
    home_score = models.IntegerField()
    away_score = models.IntegerField()
    prediction_date = models.DateTimeField(auto_now_add=True, db_index=True)
    confidence = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)  # For non-authenticated users
    
    # Additional fields for better prediction storage
    category = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    league = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    outcome = models.CharField(max_length=20, blank=True, null=True, db_index=True)  # Home, Draw, Away
    prob_home = models.FloatField(default=0.0)
    prob_draw = models.FloatField(default=0.0)
    prob_away = models.FloatField(default=0.0)
    model_type = models.CharField(max_length=50, blank=True, null=True)
    model1_prediction = models.TextField(blank=True, null=True)
    model2_prediction = models.TextField(blank=True, null=True)
    final_prediction = models.TextField(blank=True, null=True)
    
    # Scalability fields
    is_archived = models.BooleanField(default=False, db_index=True)
    archived_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.home_team} vs {self.away_team} - {self.home_score}:{self.away_score}"
    
    @classmethod
    def cleanup_old_predictions(cls, days_to_keep=90):
        """Archive predictions older than specified days.
        
        Args:
            days_to_keep: Number of days to keep active predictions (default: 90)
        
        Returns:
            Number of predictions archived
        """
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        old_predictions = cls.objects.filter(
            prediction_date__lt=cutoff_date,
            is_archived=False
        )
        count = old_predictions.update(
            is_archived=True,
            archived_date=timezone.now()
        )
        return count
    
    @classmethod
    def delete_archived_predictions(cls, days_archived=180):
        """Permanently delete predictions archived for more than specified days.
        
        Args:
            days_archived: Number of days after archiving to delete (default: 180)
        
        Returns:
            Number of predictions deleted
        """
        cutoff_date = timezone.now() - timedelta(days=days_archived)
        count, _ = cls.objects.filter(
            is_archived=True,
            archived_date__lt=cutoff_date
        ).delete()
        return count
    
    @classmethod
    def get_user_active_predictions(cls, user=None, session_key=None, limit=100):
        """Get active (non-archived) predictions for a user efficiently.
        
        Args:
            user: User object (for authenticated users)
            session_key: Session key (for anonymous users)
            limit: Maximum number of predictions to return
        
        Returns:
            QuerySet of active predictions
        """
        queryset = cls.objects.filter(is_archived=False)
        
        if user and user.is_authenticated:
            queryset = queryset.filter(user=user)
        elif session_key:
            queryset = queryset.filter(session_key=session_key)
        
        return queryset.order_by('-prediction_date')[:limit]
    
    class Meta:
        ordering = ['-prediction_date']
        indexes = [
            # Composite indexes for common queries
            models.Index(fields=['user', '-prediction_date']),
            models.Index(fields=['session_key', '-prediction_date']),
            models.Index(fields=['is_archived', '-prediction_date']),
            models.Index(fields=['league', '-prediction_date']),
            models.Index(fields=['outcome', '-prediction_date']),
            # Index for cleanup queries
            models.Index(fields=['is_archived', 'archived_date']),
        ]
        # Add constraint for data integrity
        constraints = [
            models.CheckConstraint(
                check=models.Q(confidence__gte=0.0) & models.Q(confidence__lte=100.0),
                name='valid_confidence_range'
            ),
        ]


class Match(models.Model):
    """Model for storing match data.
    
    Optimized for high-volume historical data queries.
    """
    home_team = models.CharField(max_length=100, db_index=True)
    away_team = models.CharField(max_length=100, db_index=True)
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    match_date = models.DateField(db_index=True)
    league = models.CharField(max_length=100, db_index=True)
    season = models.CharField(max_length=20, db_index=True)
    
    def __str__(self):
        return f"{self.home_team} vs {self.away_team} ({self.league})"
    
    class Meta:
        ordering = ['-match_date']
        indexes = [
            # Composite indexes for performance
            models.Index(fields=['home_team', '-match_date']),
            models.Index(fields=['away_team', '-match_date']),
            models.Index(fields=['league', '-match_date']),
            models.Index(fields=['home_team', 'away_team', '-match_date']),
        ]


class League(models.Model):
    """Model for storing league information."""
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100)  # 'European Leagues' or 'Others'
    country = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.category})"
    
    class Meta:
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['name']),
        ]


class Team(models.Model):
    """Model for storing team information."""
    name = models.CharField(max_length=100, unique=True)
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='teams')
    country = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.league.name})"
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['league']),
        ]
