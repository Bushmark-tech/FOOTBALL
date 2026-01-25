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
            # Index for billing/statistics queries
            models.Index(fields=['user', 'session_key', 'prediction_date']),
        ]
        constraints = [
            # Temporal fix for Django 5.2 CheckConstraint compatibility
            # models.CheckConstraint(
            #     check=models.Q(confidence__gte=0.0, confidence__lte=100.0),
            #     name='valid_confidence_range'
            # ),
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


class BillingUsage(models.Model):
    """Model for tracking usage statistics for billing purposes.
    
    Tracks predictions, teams, and leagues per user/session accurately.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    
    # Statistics tracked
    total_predictions = models.IntegerField(default=0, db_index=True)
    unique_teams_count = models.IntegerField(default=0)
    unique_leagues_count = models.IntegerField(default=0)
    
    # Timestamps
    first_prediction_date = models.DateTimeField(null=True, blank=True)
    last_prediction_date = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True, db_index=True)
    
    # Session tracking
    session_start = models.DateTimeField(auto_now_add=True)
    session_end = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        unique_together = [['user', 'session_key']]
        indexes = [
            models.Index(fields=['user', 'is_active', '-last_updated']),
            models.Index(fields=['session_key', 'is_active', '-last_updated']),
            models.Index(fields=['is_active', '-last_updated']),
        ]
    
    def __str__(self):
        identifier = self.user.username if self.user else f"Session: {self.session_key[:8]}"
        return f"{identifier} - {self.total_predictions} predictions"
    
    @classmethod
    def get_or_create_usage(cls, user=None, session_key=None):
        """Get or create a billing usage record for a user/session.
        
        Returns:
            tuple: (usage_object, created_boolean) or (None, False) if no user/session
        """
        if user and user.is_authenticated:
            usage, created = cls.objects.get_or_create(
                user=user,
                session_key=None,
                defaults={'is_active': True}
            )
            return usage, created
        elif session_key:
            usage, created = cls.objects.get_or_create(
                user=None,
                session_key=session_key,
                defaults={'is_active': True}
            )
            return usage, created
        else:
            return None, False
    
    def update_statistics(self):
        """Update statistics from actual predictions in database."""
        from django.db.models import Count, Q
        
        # Get predictions for this user/session
        if self.user:
            predictions = Prediction.objects.filter(
                user=self.user,
                is_archived=False
            )
        elif self.session_key:
            predictions = Prediction.objects.filter(
                session_key=self.session_key,
                is_archived=False
            )
        else:
            return
        
        # Update total predictions count
        self.total_predictions = predictions.count()
        
        # Get unique teams count
        if self.total_predictions > 0:
            home_teams = predictions.values_list('home_team', flat=True).distinct()
            away_teams = predictions.values_list('away_team', flat=True).distinct()
            all_teams = set(list(home_teams) + list(away_teams))
            self.unique_teams_count = len(all_teams)
            
            # Get unique leagues count
            self.unique_leagues_count = predictions.exclude(
                league__isnull=True
            ).exclude(
                league=''
            ).values_list('league', flat=True).distinct().count()
            
            # Update timestamps
            first_pred = predictions.order_by('prediction_date').first()
            last_pred = predictions.order_by('-prediction_date').first()
            
            if first_pred:
                self.first_prediction_date = first_pred.prediction_date
            if last_pred:
                self.last_prediction_date = last_pred.prediction_date
        
        self.save()
    
    def get_billing_summary(self):
        """Get a summary for billing purposes."""
        return {
            'user_id': self.user.id if self.user else None,
            'session_key': self.session_key,
            'total_predictions': self.total_predictions,
            'unique_teams': self.unique_teams_count,
            'unique_leagues': self.unique_leagues_count,
            'first_prediction': self.first_prediction_date.isoformat() if self.first_prediction_date else None,
            'last_prediction': self.last_prediction_date.isoformat() if self.last_prediction_date else None,
            'session_duration': (self.last_prediction_date - self.first_prediction_date).total_seconds() / 3600 if (self.first_prediction_date and self.last_prediction_date) else 0,
        }


class UserProfile(models.Model):
    """Extended user profile with subscription and free matches tracking."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    free_matches_used = models.IntegerField(default=0)
    free_matches_limit = models.IntegerField(default=1)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    mpesa_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Email verification fields
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True, unique=True)
    token_created_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.free_matches_used}/{self.free_matches_limit} free matches"
    
    def has_free_matches(self):
        """Check if user has remaining free matches."""
        return self.free_matches_used < self.free_matches_limit
    
    def get_remaining_free_matches(self):
        """Get remaining free matches."""
        return max(0, self.free_matches_limit - self.free_matches_used)
    
    def use_free_match(self):
        """Use one free match."""
        if self.has_free_matches():
            self.free_matches_used += 1
            self.save()
            return True
        return False
    
    def generate_verification_token(self):
        """Generate a unique verification token."""
        import secrets
        from django.utils import timezone
        self.verification_token = secrets.token_urlsafe(32)
        self.token_created_at = timezone.now()
        self.save()
        return self.verification_token
    
    def is_token_valid(self):
        """Check if verification token is still valid (24 hours)."""
        from django.utils import timezone
        from datetime import timedelta
        if not self.token_created_at:
            return False
        expiry_time = self.token_created_at + timedelta(hours=24)
        return timezone.now() < expiry_time
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'free_matches_used']),
            models.Index(fields=['verification_token']),
        ]


class Subscription(models.Model):
    """Model for user subscriptions."""
    SUBSCRIPTION_STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending Payment'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='mpesa')
    plan_type = models.CharField(max_length=20, default='standard')  # standard, starter, vip
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')  # USD or KSH
    mpesa_number = models.CharField(max_length=20, blank=True, null=True)
    mpesa_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.status} - {self.amount} {self.currency}"
    
    def is_active(self):
        """Check if subscription is currently active."""
        if self.status != 'active':
            return False
        if self.end_date and timezone.now() > self.end_date:
            self.status = 'expired'
            self.save()
            return False
        return True
    
    def activate(self, duration_days=30):
        """Activate subscription for specified duration."""
        self.status = 'active'
        self.start_date = timezone.now()
        self.end_date = timezone.now() + timedelta(days=duration_days)
        self.save()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status', '-created_at']),
            models.Index(fields=['status', 'end_date']),
            models.Index(fields=['mpesa_transaction_id']),
        ]
