from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum, Q
from django.utils import timezone
from .models import Team, Match, Prediction, BillingUsage, UserProfile, Subscription, League


class PredictionInline(admin.TabularInline):
    """Inline predictions for user admin"""
    model = Prediction
    extra = 0
    readonly_fields = ['home_team', 'away_team', 'prediction_date', 'confidence']
    can_delete = False
    fields = ['home_team', 'away_team', 'prediction_date', 'confidence', 'league', 'outcome']


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    """Enhanced admin for managing predictions"""
    list_display = ['match_info', 'prediction_date', 'confidence_display', 'league', 'outcome', 'user_display', 'is_archived']
    list_filter = ['is_archived', 'outcome', 'league', 'prediction_date', 'model_type']
    search_fields = ['home_team', 'away_team', 'league', 'user__username']
    readonly_fields = ['prediction_date', 'archived_date', 'created_info']
    
    fieldsets = (
        ('Match Information', {
            'fields': ('home_team', 'away_team', 'home_score', 'away_score', 'league', 'prediction_date')
        }),
        ('Prediction Details', {
            'fields': ('category', 'outcome', 'confidence', 'model_type')
        }),
        ('Probabilities', {
            'fields': ('prob_home', 'prob_draw', 'prob_away'),
            'classes': ('collapse',)
        }),
        ('Model Predictions', {
            'fields': ('model1_prediction', 'model2_prediction', 'final_prediction'),
            'classes': ('collapse',)
        }),
        ('User Information', {
            'fields': ('user', 'session_key')
        }),
        ('Archive Information', {
            'fields': ('is_archived', 'archived_date', 'created_info'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'prediction_date'
    actions = ['archive_predictions', 'unarchive_predictions', 'delete_selected']
    
    def match_info(self, obj):
        """Display match information"""
        return f"{obj.home_team} vs {obj.away_team}"
    match_info.short_description = "Match"
    
    def confidence_display(self, obj):
        """Display confidence with color coding"""
        if obj.confidence >= 80:
            color = 'green'
        elif obj.confidence >= 60:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, obj.confidence
        )
    confidence_display.short_description = "Confidence"
    
    def user_display(self, obj):
        """Display user with link"""
        if obj.user:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:auth_user_change', args=[obj.user.id]),
                obj.user.username
            )
        return "Anonymous"
    user_display.short_description = "User"
    
    def created_info(self, obj):
        """Display creation info"""
        return obj.prediction_date.strftime("%Y-%m-%d %H:%M:%S")
    created_info.short_description = "Created"
    
    def archive_predictions(self, request, queryset):
        """Archive selected predictions"""
        count = queryset.update(is_archived=True, archived_date=timezone.now())
        self.message_user(request, f"{count} predictions archived.")
    archive_predictions.short_description = "Archive selected predictions"
    
    def unarchive_predictions(self, request, queryset):
        """Unarchive selected predictions"""
        count = queryset.update(is_archived=False, archived_date=None)
        self.message_user(request, f"{count} predictions unarchived.")
    unarchive_predictions.short_description = "Unarchive selected predictions"


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Enhanced admin for team management"""
    list_display = ['name', 'league', 'country', 'match_count']
    list_filter = ['league', 'country']
    search_fields = ['name', 'league__name']
    readonly_fields = ['match_count']
    
    fieldsets = (
        ('Team Information', {
            'fields': ('name', 'league', 'country')
        }),
        ('Statistics', {
            'fields': ('match_count',),
            'classes': ('collapse',)
        }),
    )
    
    def match_count(self, obj):
        """Display number of matches"""
        count = Match.objects.filter(
            Q(home_team=obj.name) | Q(away_team=obj.name)
        ).count()
        return count
    match_count.short_description = "Matches"


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    """Enhanced admin for match management"""
    list_display = ['match_info', 'match_date', 'score_display', 'league', 'season']
    list_filter = ['league', 'season', 'match_date']
    search_fields = ['home_team', 'away_team', 'league', 'season']
    readonly_fields = ['match_date']
    
    fieldsets = (
        ('Match Information', {
            'fields': ('home_team', 'away_team', 'league', 'season', 'match_date')
        }),
        ('Score', {
            'fields': ('home_score', 'away_score')
        }),
    )
    
    date_hierarchy = 'match_date'
    
    def match_info(self, obj):
        """Display match info"""
        return f"{obj.home_team} vs {obj.away_team}"
    match_info.short_description = "Match"
    
    def score_display(self, obj):
        """Display score with formatting"""
        if obj.home_score is not None and obj.away_score is not None:
            return f"{obj.home_score} - {obj.away_score}"
        return "Not played"
    score_display.short_description = "Score"


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    """Admin for league management"""
    list_display = ['name', 'category', 'country', 'team_count']
    list_filter = ['category', 'country']
    search_fields = ['name', 'country']
    
    def team_count(self, obj):
        """Display number of teams"""
        return obj.teams.count()
    team_count.short_description = "Teams"


@admin.register(BillingUsage)
class BillingUsageAdmin(admin.ModelAdmin):
    """Enhanced admin for billing tracking"""
    list_display = ['user_or_session', 'total_predictions', 'unique_teams_count', 'unique_leagues_count', 'is_active', 'last_updated']
    list_filter = ['is_active', 'last_updated']
    search_fields = ['user__username', 'session_key']
    readonly_fields = ['session_start', 'first_prediction_date', 'last_prediction_date', 'created_info']
    
    fieldsets = (
        ('User/Session Information', {
            'fields': ('user', 'session_key', 'is_active')
        }),
        ('Usage Statistics', {
            'fields': ('total_predictions', 'unique_teams_count', 'unique_leagues_count')
        }),
        ('Timestamps', {
            'fields': ('session_start', 'session_end', 'first_prediction_date', 'last_prediction_date', 'last_updated')
        }),
    )
    
    actions = ['mark_inactive', 'mark_active']
    
    def user_or_session(self, obj):
        """Display user or session"""
        if obj.user:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:auth_user_change', args=[obj.user.id]),
                obj.user.username
            )
        return f"Session: {obj.session_key[:8]}..."
    user_or_session.short_description = "User/Session"
    
    def created_info(self, obj):
        """Display session start info"""
        return obj.session_start.strftime("%Y-%m-%d %H:%M:%S")
    created_info.short_description = "Session Started"
    
    def mark_inactive(self, request, queryset):
        """Mark sessions as inactive"""
        count = queryset.update(is_active=False, session_end=timezone.now())
        self.message_user(request, f"{count} sessions marked as inactive.")
    mark_inactive.short_description = "Mark selected as inactive"
    
    def mark_active(self, request, queryset):
        """Mark sessions as active"""
        count = queryset.update(is_active=True, session_end=None)
        self.message_user(request, f"{count} sessions marked as active.")
    mark_active.short_description = "Mark selected as active"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Enhanced admin for user profiles"""
    list_display = ['user', 'free_matches_used', 'free_matches_limit', 'payment_method_display', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'mpesa_number']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Free Tier', {
            'fields': ('free_matches_used', 'free_matches_limit', 'free_access_until')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'mpesa_number', 'mpesa_wallet')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['reset_free_quota', 'grant_free_month']
    
    def payment_method_display(self, obj):
        """Display payment method with color"""
        colors = {'mpesa': 'green', 'card': 'blue', 'none': 'gray'}
        color = colors.get(obj.payment_method, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_payment_method_display()
        )
    payment_method_display.short_description = "Payment Method"
    
    def reset_free_quota(self, request, queryset):
        """Reset free matches quota"""
        count = queryset.update(free_matches_used=0)
        self.message_user(request, f"Reset quota for {count} users.")
    reset_free_quota.short_description = "Reset free quota"
    
    def grant_free_month(self, request, queryset):
        """Grant free access for 30 days"""
        end_date = timezone.now() + timezone.timedelta(days=30)
        count = queryset.update(free_access_until=end_date)
        self.message_user(request, f"Granted free month to {count} users.")
    grant_free_month.short_description = "Grant 30 days free access"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Enhanced admin for subscription management"""
    list_display = ['user', 'status_display', 'amount_display', 'payment_method', 'start_date', 'end_date', 'days_remaining']
    list_filter = ['status', 'payment_method', 'currency', 'created_at', 'start_date']
    search_fields = ['user__username', 'mpesa_transaction_id', 'mpesa_number']
    readonly_fields = ['created_at', 'updated_at', 'days_remaining_info']
    
    fieldsets = (
        ('Subscription Information', {
            'fields': ('user', 'status', 'payment_method')
        }),
        ('Payment Details', {
            'fields': ('amount', 'currency')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'days_remaining_info')
        }),
        ('Payment Reference', {
            'fields': ('mpesa_number', 'mpesa_transaction_id', 'mpesa_wallet'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    date_hierarchy = 'created_at'
    actions = ['activate_subscriptions', 'cancel_subscriptions', 'extend_subscriptions']
    
    def status_display(self, obj):
        """Display status with color coding"""
        colors = {'active': 'green', 'expired': 'red', 'cancelled': 'gray', 'pending': 'orange'}
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = "Status"
    
    def amount_display(self, obj):
        """Display amount with currency"""
        return f"{obj.currency} {obj.amount}"
    amount_display.short_description = "Amount"
    
    def days_remaining(self, obj):
        """Display days remaining"""
        if obj.status == 'active' and obj.end_date:
            days = (obj.end_date - timezone.now().date()).days
            if days > 0:
                return format_html(
                    '<span style="color: green; font-weight: bold;">{} days</span>',
                    days
                )
            else:
                return format_html(
                    '<span style="color: red; font-weight: bold;">Expired</span>'
                )
        return "-"
    days_remaining.short_description = "Days Remaining"
    
    def days_remaining_info(self, obj):
        """Info display for days remaining"""
        if obj.end_date:
            days = (obj.end_date - timezone.now().date()).days
            return f"{days} days remaining" if days > 0 else "Expired"
        return "No end date"
    days_remaining_info.short_description = "Days Remaining"
    
    def activate_subscriptions(self, request, queryset):
        """Activate selected subscriptions"""
        count = queryset.update(status='active')
        self.message_user(request, f"{count} subscriptions activated.")
    activate_subscriptions.short_description = "Activate selected subscriptions"
    
    def cancel_subscriptions(self, request, queryset):
        """Cancel selected subscriptions"""
        count = queryset.update(status='cancelled')
        self.message_user(request, f"{count} subscriptions cancelled.")
    cancel_subscriptions.short_description = "Cancel selected subscriptions"
    
    def extend_subscriptions(self, request, queryset):
        """Extend subscriptions by 30 days"""
        from datetime import timedelta
        for subscription in queryset:
            if subscription.end_date:
                subscription.end_date += timedelta(days=30)
            else:
                subscription.end_date = timezone.now().date() + timedelta(days=30)
            subscription.save()
        self.message_user(request, f"Extended {queryset.count()} subscriptions by 30 days.")
    extend_subscriptions.short_description = "Extend by 30 days"


# Customize admin site
admin.site.site_header = "Football Predictor Admin"
admin.site.site_title = "Admin Dashboard"
admin.site.index_title = "Welcome to Football Predictor Administration" 
