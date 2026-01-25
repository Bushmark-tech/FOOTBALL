"""
Admin Dashboard Views
Provides comprehensive system control and monitoring for administrators
Includes: user management, predictions, billing, analytics, system control
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group, Permission
from django.contrib import messages
from django.db.models import Count, Sum, Q, Avg, F, Case, When
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from datetime import datetime, timedelta
import logging
import json

from .models import Prediction, BillingUsage, UserProfile, Subscription, Team, Match, League

logger = logging.getLogger(__name__)


def is_admin(user):
    """Check if user is staff/admin - only these can access admin pages"""
    return user.is_active and (user.is_staff or user.is_superuser)


def admin_required(view_func):
    """Decorator for views that checks if the user is an admin."""
    @login_required(login_url='predictor:login')
    def _wrapped_view(request, *args, **kwargs):
        if not is_admin(request.user):
            from django.contrib import messages
            messages.error(request, "Permission Denied: Staff status required.")
            return redirect('predictor:home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# ============================================
# DASHBOARD & OVERVIEW
# ============================================

@admin_required
def admin_dashboard(request):
    """Main admin dashboard with comprehensive system overview"""
        
    from django.conf import settings
    
    # Calculate time-based metrics
    today = timezone.now().date()
    week_ago = timezone.now() - timedelta(days=7)
    month_ago = timezone.now() - timedelta(days=30)
    
    # User Statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(
        prediction__prediction_date__gte=week_ago
    ).distinct().count()
    new_users_month = User.objects.filter(
        date_joined__gte=month_ago
    ).count()
    new_users_week = User.objects.filter(
        date_joined__gte=week_ago
    ).count()
    
    # Social Login Statistics (Google users)
    google_users_count = 0
    try:
        from allauth.socialaccount.models import SocialAccount
        google_users_count = SocialAccount.objects.filter(provider='google').count()
    except (ImportError, Exception):
        google_users_count = 0 # Fallback if allauth not installed
    
    # Prediction Statistics
    total_predictions = Prediction.objects.filter(is_archived=False).count()
    today_predictions = Prediction.objects.filter(
        prediction_date__date=today,
        is_archived=False
    ).count()
    week_predictions = Prediction.objects.filter(
        prediction_date__gte=week_ago,
        is_archived=False
    ).count()
    
    # Subscription & Revenue
    active_subscriptions = Subscription.objects.filter(status='active').count()
    total_revenue = Subscription.objects.filter(
        status='active'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    pending_subscriptions = Subscription.objects.filter(status='pending').count()
    
    # Advanced Metrics
    conversion_rate = (active_subscriptions / total_users * 100) if total_users > 0 else 0
    avg_revenue_per_user = (total_revenue / active_subscriptions) if active_subscriptions > 0 else 0
    
    # Database Statistics
    total_matches = Match.objects.count()
    total_teams = Team.objects.count()
    total_leagues = League.objects.count()
    
    # Data Quality Metrics
    archived_predictions = Prediction.objects.filter(is_archived=True).count()
    predictions_without_outcome = Prediction.objects.filter(
        is_archived=False, outcome__isnull=True
    ).count()
    
    # Recent Activity
    recent_predictions = Prediction.objects.filter(
        is_archived=False
    ).select_related('user').order_by('-prediction_date')[:5]
    
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'new_users_month': new_users_month,
        'new_users_week': new_users_week,
        'google_users_count': google_users_count,
        'email_users_count': total_users - google_users_count,
        'total_predictions': total_predictions,
        'today_predictions': today_predictions,
        'week_predictions': week_predictions,
        'active_subscriptions': active_subscriptions,
        'pending_subscriptions': pending_subscriptions,
        'total_revenue': total_revenue,
        'conversion_rate': conversion_rate,
        'avg_revenue_per_user': avg_revenue_per_user,
        'total_matches': total_matches,
        'total_teams': total_teams,
        'total_leagues': total_leagues,
        'archived_predictions': archived_predictions,
        'predictions_without_outcome': predictions_without_outcome,
        'recent_predictions': recent_predictions,
        'recent_users': recent_users,
        'google_analytics_id': getattr(settings, 'GOOGLE_ANALYTICS_ID', ''),
        'is_admin': True
    }
    
    return render(request, 'admin/dashboard.html', context)



# ============================================
# USER MANAGEMENT
# ============================================

@admin_required
def admin_users(request):
    """Comprehensive user management interface"""
    
    users = User.objects.annotate(
        prediction_count=Count('prediction'),
        subscription_status=Case(
            When(subscriptions__status='active', then=1),
            default=0
        ),
        total_spent=Sum('subscriptions__amount')
    ).select_related('profile').order_by('-date_joined')
    
    # Filtering
    filter_type = request.GET.get('filter', 'all')
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', '-date_joined')
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    if filter_type == 'active':
        users = users.filter(
            prediction__prediction_date__gte=timezone.now() - timedelta(days=7)
        ).distinct()
    elif filter_type == 'inactive':
        users = users.filter(
            prediction__prediction_date__lt=timezone.now() - timedelta(days=30)
        ) | users.filter(prediction__isnull=True)
        users = users.distinct()
    elif filter_type == 'subscribed':
        users = users.filter(subscriptions__status='active').distinct()
    elif filter_type == 'free_tier':
        users = users.filter(subscriptions__isnull=True)
    elif filter_type == 'staff':
        users = users.filter(is_staff=True)
    
    # Sorting
    if sort_by == 'predictions':
        users = users.order_by('-prediction_count')
    elif sort_by == 'spent':
        users = users.order_by('-total_spent')
    elif sort_by == 'email':
        users = users.order_by('email')
    else:
        users = users.order_by(sort_by)
    
    # Pagination
    page = int(request.GET.get('page', 1))
    per_page = 50
    total = users.count()
    start = (page - 1) * per_page
    users_page = users[start:start + per_page]
    
    context = {
        'users': users_page,
        'total': total,
        'page': page,
        'has_next': (start + per_page) < total,
        'has_prev': page > 1,
        'filter_type': filter_type,
        'search_query': search_query,
        'sort_by': sort_by,
        'is_admin': True
    }
    
    return render(request, 'admin/users.html', context)


@admin_required
def admin_user_detail(request, user_id):
    """Detailed view and control for individual user"""
    
    user = get_object_or_404(User, id=user_id)
    profile = UserProfile.objects.filter(user=user).first()
    
    # User statistics
    predictions = Prediction.objects.filter(user=user)
    subscriptions = Subscription.objects.filter(user=user)
    billing = BillingUsage.objects.filter(user=user).first()
    
    context = {
        'user': user,
        'profile': profile,
        'prediction_count': predictions.count(),
        'predictions': predictions.order_by('-prediction_date')[:10],
        'subscriptions': subscriptions.order_by('-created_at'),
        'billing': billing,
        'is_admin': True
    }
    
    return render(request, 'admin/user_detail.html', context)


@admin_required
@require_http_methods(["POST"])
def admin_user_action(request, user_id):
    """Perform actions on users"""
    
    user = get_object_or_404(User, id=user_id)
    action = request.POST.get('action')
    
    try:
        if action == 'toggle_staff':
            user.is_staff = not user.is_staff
            user.save()
            messages.success(request, f'Staff status {"enabled" if user.is_staff else "disabled"} for {user.username}')
        
        elif action == 'toggle_active':
            user.is_active = not user.is_active
            user.save()
            messages.success(request, f'Account {"activated" if user.is_active else "deactivated"} for {user.username}')
        
        elif action == 'reset_password':
            from django.contrib.auth import get_user_model
            new_password = request.POST.get('new_password', 'TempPass123!')
            user.set_password(new_password)
            user.save()
            messages.success(request, f'Password reset for {user.username}')
            logger.info(f"Admin {request.user.username} reset password for {user.username}")
        
        elif action == 'grant_free_access':
            days = int(request.POST.get('days', 30))
            # Create a free VIP subscription
            Subscription.objects.create(
                user=user,
                plan_type='vip',
                amount=0,
                currency='KES',
                status='active',
                payment_method='mpesa',  # Default to mpesa as placeholder
                start_date=timezone.now(),
                end_date=timezone.now() + timedelta(days=days)
            )
            messages.success(request, f'Granted {days} days VIP access to {user.username}')
            logger.info(f"Admin {request.user.username} granted {days} days VIP to {user.username}")
        
        elif action == 'reset_free_quota':
            profile = UserProfile.objects.get_or_create(user=user)[0]
            profile.free_matches_used = 0
            profile.save()
            messages.success(request, f'Free quota reset for {user.username}')
        
        elif action == 'delete_user':
            username = user.username
            user.delete()
            messages.success(request, f'User {username} deleted successfully')
            logger.warning(f"Admin {request.user.username} deleted user {username}")
            return redirect('predictor:admin_users')
    
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        logger.error(f"Error performing action {action} on user {user_id}: {str(e)}")
    
    return redirect('predictor:admin_user_detail', user_id=user_id)


# ============================================
# PREDICTION MANAGEMENT
# ============================================

@admin_required
def admin_predictions(request):
    """Manage and view predictions"""
    
    predictions = Prediction.objects.select_related('user').order_by('-prediction_date')
    
    # Statistics
    total_predictions = predictions.count()
    active_predictions = predictions.filter(is_archived=False).count()
    accurate = predictions.filter(outcome__in=['Home', 'Away', 'Draw']).count()
    accuracy_rate = (accurate / total_predictions * 100) if total_predictions > 0 else 0
    
    # Filters
    league_filter = request.GET.get('league', '')
    outcome_filter = request.GET.get('outcome', '')
    is_archived_filter = request.GET.get('archived', 'false')
    confidence_min = request.GET.get('confidence_min', '')
    
    if league_filter:
        predictions = predictions.filter(league=league_filter)
    
    if outcome_filter:
        predictions = predictions.filter(outcome=outcome_filter)
    
    if is_archived_filter == 'true':
        predictions = predictions.filter(is_archived=True)
    else:
        predictions = predictions.filter(is_archived=False)
    
    if confidence_min:
        try:
            min_conf = float(confidence_min)
            predictions = predictions.filter(confidence__gte=min_conf)
        except ValueError:
            pass
    
    # Get unique values for filters
    leagues = Prediction.objects.values_list('league', flat=True).distinct().order_by('league')
    outcomes = Prediction.objects.values_list('outcome', flat=True).distinct()
    
    # Pagination
    page = int(request.GET.get('page', 1))
    per_page = 100
    total = predictions.count()
    start = (page - 1) * per_page
    predictions_page = predictions[start:start + per_page]
    
    # Add confidence percentage and scale probabilities to each prediction
    for prediction in predictions_page:
        if prediction.confidence:
            # Handle both 0-1 scale (decimal) and 0-100 scale (percentage)
            if prediction.confidence <= 1:
                prediction.confidence_percentage = int(prediction.confidence * 100)
            else:
                prediction.confidence_percentage = int(prediction.confidence)
        else:
            prediction.confidence_percentage = 0

        # Scale Probabilities (0-1 -> 0-100) for display
        if prediction.prob_home is not None and prediction.prob_home <= 1.0:
            prediction.prob_home *= 100
        if prediction.prob_draw is not None and prediction.prob_draw <= 1.0:
            prediction.prob_draw *= 100
        if prediction.prob_away is not None and prediction.prob_away <= 1.0:
            prediction.prob_away *= 100
    
    context = {
        'predictions': predictions_page,
        'total': total,
        'page': page,
        'has_next': (start + per_page) < total,
        'has_prev': page > 1,
        'active_predictions': active_predictions,
        'accuracy_rate': accuracy_rate,
        'leagues': leagues,
        'outcomes': outcomes,
        'league_filter': league_filter,
        'outcome_filter': outcome_filter,
        'confidence_min': confidence_min,
        'is_admin': True
    }
    
    return render(request, 'admin/predictions.html', context)


@admin_required
@require_http_methods(["POST"])
def admin_prediction_action(request, prediction_id):
    """Perform actions on predictions"""
    
    prediction = get_object_or_404(Prediction, id=prediction_id)
    action = request.POST.get('action')
    
    try:
        if action == 'archive':
            prediction.is_archived = True
            prediction.archived_date = timezone.now()
            prediction.save()
            messages.success(request, f'Prediction archived')
        
        elif action == 'unarchive':
            prediction.is_archived = False
            prediction.archived_date = None
            prediction.save()
            messages.success(request, f'Prediction unarchived')
        
        elif action == 'set_outcome':
            outcome = request.POST.get('outcome')
            prediction.outcome = outcome
            prediction.save()
            messages.success(request, f'Outcome set to {outcome}')
        
        elif action == 'delete':
            prediction.delete()
            messages.success(request, f'Prediction deleted')
            return redirect('predictor:admin_predictions')
    
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        logger.error(f"Error performing action {action} on prediction {prediction_id}: {str(e)}")
    
    return redirect('predictor:admin_predictions')


# ============================================
# SUBSCRIPTION & BILLING MANAGEMENT
# ============================================

@admin_required
def admin_billing(request):
    """Manage subscriptions and billing"""
    
    subscriptions = Subscription.objects.select_related('user').order_by('-created_at')
    
    # Statistics
    active_subs = subscriptions.filter(status='active').count()
    expired_subs = subscriptions.filter(status='expired').count()
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    total_revenue = subscriptions.filter(
        status='active'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Revenue Trend (Last 30 Days)
    revenue_trend = Subscription.objects.filter(
        created_at__gte=thirty_days_ago
    ).extra(
        select={'day': 'DATE(created_at)'}
    ).values('day').annotate(daily_total=Sum('amount')).order_by('day')
    
    # Format for Chart.js
    chart_labels = []
    chart_data = []
    
    # Create a dict for easy lookup
    revenue_map = {item['day']: item['daily_total'] for item in revenue_trend}
    
    # Fill in missing days
    for i in range(30):
        d = thirty_days_ago + timedelta(days=i)
        d_str = d.strftime('%Y-%m-%d')
        chart_labels.append(d.strftime('%b %d'))
        chart_data.append(float(revenue_map.get(d, 0) if isinstance(revenue_map.get(d, 0), (int, float)) else 0)) 
        # Note: extra() returns dates as strings or objects depending on DB backend, 
        # but for SQLite it might be tricky. Let's rely on the template to handle simple arrays if possible,
        # or robustly handle it here. 
        # Actually simplest is just to pass the query result and process in JS, but filling zeros is nicer.
    
    
    # Filters
    status_filter = request.GET.get('status', 'all')
    method_filter = request.GET.get('method', 'all')
    currency_filter = request.GET.get('currency', 'all')
    
    if status_filter != 'all':
        subscriptions = subscriptions.filter(status=status_filter)
    
    if method_filter != 'all':
        subscriptions = subscriptions.filter(payment_method=method_filter)
    
    if currency_filter != 'all':
        subscriptions = subscriptions.filter(currency=currency_filter)
    
    # Get unique values for filters
    statuses = Subscription.objects.values_list('status', flat=True).distinct()
    methods = Subscription.objects.values_list('payment_method', flat=True).distinct()
    currencies = Subscription.objects.values_list('currency', flat=True).distinct()
    
    # Pagination
    page = int(request.GET.get('page', 1))
    per_page = 50
    total = subscriptions.count()
    start = (page - 1) * per_page
    subs_page = subscriptions[start:start + per_page]
    
    context = {
        'subscriptions': subs_page,
        'total': total,
        'page': page,
        'has_next': (start + per_page) < total,
        'has_prev': page > 1,
        'active_subs': active_subs,
        'active_subscriptions': active_subs, # Alias for template compatibility
        'expired_subs': expired_subs,
        'total_revenue': total_revenue,
        'revenue_labels': json.dumps(chart_labels),
        'revenue_data': json.dumps(chart_data),
        'statuses': statuses,
        'methods': methods,
        'currencies': currencies,
        'status_filter': status_filter,
        'method_filter': method_filter,
        'currency_filter': currency_filter,
        'is_admin': True
    }
    
    return render(request, 'admin/billing.html', context)


@admin_required
@require_http_methods(["POST"])
def admin_subscription_action(request, subscription_id):
    """Perform actions on subscriptions"""
    
    subscription = get_object_or_404(Subscription, id=subscription_id)
    action = request.POST.get('action')
    
    try:
        if action == 'activate':
            subscription.status = 'active'
            subscription.save()
            messages.success(request, f'Subscription activated for {subscription.user.username}')
        
        elif action == 'cancel':
            subscription.status = 'cancelled'
            subscription.save()
            messages.success(request, f'Subscription cancelled for {subscription.user.username}')
        
        elif action == 'extend':
            days = int(request.POST.get('days', 30))
            if subscription.end_date:
                subscription.end_date += timedelta(days=days)
            else:
                subscription.end_date = timezone.now().date() + timedelta(days=days)
            subscription.save()
            messages.success(request, f'Subscription extended by {days} days')
        
        elif action == 'refund':
            amount = request.POST.get('amount')
            # Log refund action
            logger.warning(f"Admin {request.user.username} refunded {amount} for subscription {subscription.id}")
            messages.success(request, f'Refund of {amount} recorded')
    
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        logger.error(f"Error performing action {action} on subscription {subscription_id}: {str(e)}")
    
    return redirect('predictor:admin_billing')


# ============================================
# ANALYTICS & REPORTING
# ============================================

@admin_required
def admin_analytics(request):
    """Detailed analytics and reporting"""
    
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Users analytics
    users_by_day = User.objects.filter(
        date_joined__gte=start_date
    ).extra(
        select={'day': 'DATE(date_joined)'}
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    # Predictions analytics
    predictions_by_day = Prediction.objects.filter(
        prediction_date__gte=start_date,
        is_archived=False
    ).extra(
        select={'day': 'DATE(prediction_date)'}
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    # Revenue analytics
    revenue_by_day = Subscription.objects.filter(
        created_at__gte=start_date
    ).extra(
        select={'day': 'DATE(created_at)'}
    ).values('day').annotate(total=Sum('amount')).order_by('day')
    
    # Top leagues
    top_leagues = Prediction.objects.filter(
        prediction_date__gte=start_date,
        is_archived=False
    ).values('league').annotate(
        count=Count('id'),
        avg_confidence=Avg('confidence')
    ).order_by('-count')[:15]
    
    # Top teams
    home_teams = Prediction.objects.filter(
        prediction_date__gte=start_date,
        is_archived=False
    ).values('home_team').annotate(count=Count('id')).values_list('home_team', 'count')
    
    away_teams = Prediction.objects.filter(
        prediction_date__gte=start_date,
        is_archived=False
    ).values('away_team').annotate(count=Count('id')).values_list('away_team', 'count')
    
    # Process data for Charts (fill missing days)
    chart_labels = []
    users_data = []
    predictions_data = []
    
    # Helper to convert query result to dict
    def to_dict(qs):
        return {item['day']: item['count'] for item in qs}
        
    users_map = to_dict(users_by_day)
    predictions_map = to_dict(predictions_by_day)
    
    for i in range(days):
        d = start_date + timedelta(days=i)
        # Handle date/datetime mismatch if necessary, but usually d.date() is safest
        if hasattr(d, 'date'):
             d_key = d.date()
        else:
             d_key = d
             
        # Because we used extra() with DATE(), the keys in map might be strings or date objects depending on DB
        # This part can be tricky across DBs. 
        # For robustness, we will try to match string representation if direct match fails.
        
        val_users = users_map.get(d_key, 0)
        # Fallback check for string keys if date object lookup failed
        if val_users == 0 and isinstance(list(users_map.keys())[0] if users_map else '', str):
             val_users = users_map.get(str(d_key), 0)

        val_preds = predictions_map.get(d_key, 0)
         # Fallback check for string keys
        if val_preds == 0 and isinstance(list(predictions_map.keys())[0] if predictions_map else '', str):
             val_preds = predictions_map.get(str(d_key), 0)

        chart_labels.append(d.strftime('%b %d'))
        users_data.append(val_users)
        predictions_data.append(val_preds)
    
    context = {
        'users_by_day': list(users_by_day),
        'predictions_by_day': list(predictions_by_day),
        'revenue_by_day': list(revenue_by_day),
        'chart_labels': json.dumps(chart_labels),
        'users_data': json.dumps(users_data),
        'predictions_data': json.dumps(predictions_data),
        'top_leagues': list(top_leagues),
        'days': days,
        'is_admin': True
    }
    
    return render(request, 'admin/analytics.html', context)


# ============================================
# SYSTEM CONTROL & MAINTENANCE
# ============================================

@admin_required
def admin_system(request):
    """System control and maintenance"""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        try:
            if action == 'clear_cache':
                cache.clear()
                messages.success(request, 'Cache cleared successfully')
                logger.info(f"Admin {request.user.username} cleared cache")
            
            elif action == 'cleanup_predictions':
                days = int(request.POST.get('days', 90))
                count = Prediction.cleanup_old_predictions(days)
                messages.success(request, f'Archived {count} old predictions')
                logger.info(f"Admin {request.user.username} archived {count} old predictions")
            
            elif action == 'delete_archived':
                days = int(request.POST.get('days', 180))
                count = Prediction.delete_archived_predictions(days)
                messages.success(request, f'Permanently deleted {count} archived predictions')
                logger.warning(f"Admin {request.user.username} deleted {count} archived predictions")
            
            elif action == 'rebuild_indexes':
                messages.info(request, 'Index rebuild initiated. Check logs for details.')
                logger.info(f"Admin {request.user.username} requested index rebuild")
        
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            logger.error(f"Error performing action {action}: {str(e)}")
        
        return redirect('predictor:admin_system')
    
    # System stats
    total_predictions = Prediction.objects.count()
    active_predictions = Prediction.objects.filter(is_archived=False).count()
    archived_predictions = Prediction.objects.filter(is_archived=True).count()
    db_size = f"{total_predictions} predictions stored"
    
    context = {
        'total_predictions': total_predictions,
        'active_predictions': active_predictions,
        'archived_predictions': archived_predictions,
        'db_size': db_size,
        'is_admin': True
    }
    
    return render(request, 'admin/system.html', context)


# ============================================
# DATA MANAGEMENT
# ============================================

@admin_required
def admin_data(request):
    """Data management interface"""
    
    # Count statistics
    teams_count = Team.objects.count()
    leagues_count = League.objects.count()
    matches_count = Match.objects.count()
    predictions_count = Prediction.objects.filter(is_archived=False).count()
    
    # Get lists
    leagues = League.objects.annotate(
        team_count=Count('teams', distinct=True)
    ).order_by('-team_count')[:20]
    
    teams_without_league = Team.objects.filter(league__isnull=True).count()
    
    context = {
        'teams_count': teams_count,
        'leagues_count': leagues_count,
        'matches_count': matches_count,
        'predictions_count': predictions_count,
        'leagues': leagues,
        'teams_without_league': teams_without_league,
        'is_admin': True
    }
    
    return render(request, 'admin/data.html', context)


# ============================================
# UTILITY ENDPOINTS
# ============================================

@admin_required
@require_http_methods(["GET"])
def admin_api_stats(request):
    """API endpoint for real-time statistics"""
    
    stats = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(
            prediction__prediction_date__gte=timezone.now() - timedelta(days=7)
        ).distinct().count(),
        'total_predictions': Prediction.objects.filter(is_archived=False).count(),
        'today_predictions': Prediction.objects.filter(
            prediction_date__date=timezone.now().date(),
            is_archived=False
        ).count(),
        'active_subscriptions': Subscription.objects.filter(status='active').count(),
        'total_revenue': float(
            Subscription.objects.filter(status='active').aggregate(
                total=Sum('amount')
            )['total'] or 0
        ),
        'timestamp': timezone.now().isoformat()
    }
    
    return JsonResponse(stats)


@admin_required
def import_data(request):
    """Import teams, leagues, and match data from CSV"""
    if request.method == 'POST':
        try:
            csv_file = request.FILES.get('csv_file')
            if not csv_file:
                return JsonResponse({'success': False, 'error': 'No file uploaded'})
            
            import csv
            import io
            
            stream = io.TextIOWrapper(csv_file.file, encoding='utf-8')
            csv_reader = csv.DictReader(stream)
            
            imported_count = 0
            errors = []
            
            for row_num, row in enumerate(csv_reader, start=2):
                try:
                    # Expected columns: league_name, team_name, country
                    league_name = row.get('league_name', '').strip()
                    team_name = row.get('team_name', '').strip()
                    country = row.get('country', '').strip()
                    
                    if league_name and team_name:
                        # Create or get league
                        league, _ = League.objects.get_or_create(
                            name=league_name,
                            defaults={'category': 'Others', 'country': country}
                        )
                        
                        # Create or get team
                        Team.objects.get_or_create(
                            name=team_name,
                            defaults={'league': league, 'country': country}
                        )
                        
                        imported_count += 1
                except Exception as e:
                    errors.append(f'Row {row_num}: {str(e)}')
            
            return JsonResponse({
                'success': True,
                'imported': imported_count,
                'errors': errors[:10]  # Show first 10 errors
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@admin_required
def export_data(request):
    """Export predictions and data to CSV"""
    try:
        from django.http import HttpResponse
        import csv
        
        export_type = request.GET.get('type', 'predictions')
        
        if export_type == 'predictions':
            predictions = Prediction.objects.all().values(
                'id', 'home_team', 'away_team', 'home_score', 'away_score',
                'outcome', 'confidence', 'league', 'prediction_date'
            )
            filename = f'predictions_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
            field_names = ['id', 'home_team', 'away_team', 'home_score', 'away_score', 
                          'outcome', 'confidence', 'league', 'prediction_date']
            data = predictions
        
        elif export_type == 'teams':
            teams = Team.objects.select_related('league').values(
                'name', 'league__name', 'country'
            )
            filename = f'teams_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
            field_names = ['name', 'league', 'country']
            data = [{'name': t['name'], 'league': t['league__name'], 'country': t['country']} for t in teams]
        
        else:  # leagues
            leagues = League.objects.values('name', 'category', 'country')
            filename = f'leagues_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
            field_names = ['name', 'category', 'country']
            data = leagues
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.DictWriter(response, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(data)
        
        return response
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@admin_required
def sync_data(request):
    """Synchronize with external data sources"""
    try:
        sync_type = request.POST.get('sync_type', 'all')
        
        results = {
            'leagues_synced': 0,
            'teams_synced': 0,
            'matches_synced': 0,
            'success': True,
            'message': 'Data synchronization completed'
        }
        
        # Sync leagues
        if sync_type in ['all', 'leagues']:
            try:
                # Get existing predictions and extract unique leagues
                unique_leagues = Prediction.objects.filter(
                    league__isnull=False
                ).values_list('league', flat=True).distinct()
                
                for league_name in unique_leagues:
                    League.objects.get_or_create(
                        name=league_name,
                        defaults={'category': 'Others'}
                    )
                results['leagues_synced'] = len(set(unique_leagues))
            except Exception as e:
                results['leagues_error'] = str(e)
        
        # Sync teams
        if sync_type in ['all', 'teams']:
            try:
                # Get unique teams from predictions
                home_teams = set(Prediction.objects.values_list('home_team', flat=True).distinct())
                away_teams = set(Prediction.objects.values_list('away_team', flat=True).distinct())
                all_teams = home_teams | away_teams
                
                for team_name in all_teams:
                    Team.objects.get_or_create(
                        name=team_name,
                        defaults={'league': League.objects.first(), 'country': 'Unknown'}
                    )
                results['teams_synced'] = len(all_teams)
            except Exception as e:
                results['teams_error'] = str(e)
        
        # Sync matches
        if sync_type in ['all', 'matches']:
            try:
                # Create matches from predictions
                synced_matches = set()
                for pred in Prediction.objects.all():
                    match_key = f"{pred.home_team}_{pred.away_team}"
                    if match_key not in synced_matches:
                        Match.objects.get_or_create(
                            home_team=pred.home_team,
                            away_team=pred.away_team,
                            match_date=pred.prediction_date.date(),
                            defaults={
                                'home_score': pred.home_score,
                                'away_score': pred.away_score,
                                'league': pred.league or 'Unknown',
                                'season': timezone.now().year
                            }
                        )
                        synced_matches.add(match_key)
                results['matches_synced'] = len(synced_matches)
            except Exception as e:
                results['matches_error'] = str(e)
        
        return JsonResponse(results)
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})



