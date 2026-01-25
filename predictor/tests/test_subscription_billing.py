"""
Unit tests for Subscription and Billing functionality
Tests subscription lifecycle, expiration, payment processing, and access control
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from predictor.models import Subscription, UserProfile, BillingUsage


class SubscriptionModelTest(TestCase):
    """Test Subscription model functionality"""
    
    def setUp(self):
        """Set up test user and subscription"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@gmail.com',
            password='pass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            free_matches_limit=1
        )
    
    def test_create_subscription(self):
        """Test creating a new subscription"""
        subscription = Subscription.objects.create(
            user=self.user,
            status='pending',
            payment_method='mpesa',
            plan_type='standard',
            amount=Decimal('200.00'),
            currency='KSH'
        )
        
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.status, 'pending')
        self.assertEqual(subscription.plan_type, 'standard')
        self.assertEqual(subscription.amount, Decimal('200.00'))
        print("✓ Subscription creation works")
    
    def test_subscription_activation(self):
        """Test activating a subscription"""
        subscription = Subscription.objects.create(
            user=self.user,
            status='pending',
            payment_method='mpesa',
            plan_type='standard',
            amount=Decimal('200.00'),
            currency='KSH'
        )
        
        # Activate for 30 days
        subscription.activate(duration_days=30)
        
        self.assertEqual(subscription.status, 'active')
        self.assertIsNotNone(subscription.start_date)
        self.assertIsNotNone(subscription.end_date)
        
        # Check end_date is 30 days from start_date
        expected_end = subscription.start_date + timedelta(days=30)
        self.assertEqual(subscription.end_date.date(), expected_end.date())
        print("✓ Subscription activation works")
    
    def test_subscription_is_active_when_valid(self):
        """Test is_active() returns True for valid subscription"""
        subscription = Subscription.objects.create(
            user=self.user,
            status='active',
            payment_method='mpesa',
            plan_type='standard',
            amount=Decimal('200.00'),
            currency='KSH',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=15)  # 15 days remaining
        )
        
        self.assertTrue(subscription.is_active())
        print("✓ Active subscription detected correctly")
    
    def test_subscription_expires_automatically(self):
        """Test subscription auto-expires when end_date passes"""
        subscription = Subscription.objects.create(
            user=self.user,
            status='active',
            payment_method='mpesa',
            plan_type='standard',
            amount=Decimal('200.00'),
            currency='KSH',
            start_date=timezone.now() - timedelta(days=31),
            end_date=timezone.now() - timedelta(days=1)  # Expired yesterday
        )
        
        # Check is_active() - should auto-expire
        is_active = subscription.is_active()
        
        self.assertFalse(is_active)
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, 'expired')
        print("✓ Subscription auto-expires correctly")
    
    def test_subscription_not_active_when_pending(self):
        """Test is_active() returns False for pending subscription"""
        subscription = Subscription.objects.create(
            user=self.user,
            status='pending',
            payment_method='mpesa',
            plan_type='standard',
            amount=Decimal('200.00'),
            currency='KSH'
        )
        
        self.assertFalse(subscription.is_active())
        print("✓ Pending subscription not active")
    
    def test_subscription_not_active_when_cancelled(self):
        """Test is_active() returns False for cancelled subscription"""
        subscription = Subscription.objects.create(
            user=self.user,
            status='cancelled',
            payment_method='mpesa',
            plan_type='standard',
            amount=Decimal('200.00'),
            currency='KSH',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=15)
        )
        
        self.assertFalse(subscription.is_active())
        print("✓ Cancelled subscription not active")
    
    def test_get_daily_limit_standard(self):
        """Test daily limit for standard plan"""
        subscription = Subscription.objects.create(
            user=self.user,
            plan_type='standard',
            amount=Decimal('200.00'),
            currency='KSH'
        )
        
        self.assertEqual(subscription.get_daily_limit(), 7)
        print("✓ Standard plan daily limit: 7")
    
    def test_get_daily_limit_starter(self):
        """Test daily limit for starter plan"""
        subscription = Subscription.objects.create(
            user=self.user,
            plan_type='starter',
            amount=Decimal('500.00'),
            currency='KSH'
        )
        
        self.assertEqual(subscription.get_daily_limit(), 20)
        print("✓ Starter plan daily limit: 20")
    
    def test_get_daily_limit_vip(self):
        """Test daily limit for VIP plan"""
        subscription = Subscription.objects.create(
            user=self.user,
            plan_type='vip',
            amount=Decimal('1000.00'),
            currency='KSH'
        )
        
        self.assertEqual(subscription.get_daily_limit(), 100)
        print("✓ VIP plan daily limit: 100")
    
    def test_get_monthly_limit_standard(self):
        """Test monthly limit for standard plan"""
        subscription = Subscription.objects.create(
            user=self.user,
            plan_type='standard',
            amount=Decimal('200.00'),
            currency='KSH'
        )
        
        self.assertEqual(subscription.get_monthly_limit(), 300)
        print("✓ Standard plan monthly limit: 300")
    
    def test_get_monthly_limit_starter(self):
        """Test monthly limit for starter plan"""
        subscription = Subscription.objects.create(
            user=self.user,
            plan_type='starter',
            amount=Decimal('500.00'),
            currency='KSH'
        )
        
        self.assertEqual(subscription.get_monthly_limit(), 600)
        print("✓ Starter plan monthly limit: 600")
    
    def test_get_monthly_limit_vip(self):
        """Test monthly limit for VIP plan"""
        subscription = Subscription.objects.create(
            user=self.user,
            plan_type='vip',
            amount=Decimal('1000.00'),
            currency='KSH'
        )
        
        self.assertEqual(subscription.get_monthly_limit(), 1500)
        print("✓ VIP plan monthly limit: 1500")
    
    def test_subscription_string_representation(self):
        """Test subscription __str__ method"""
        subscription = Subscription.objects.create(
            user=self.user,
            status='active',
            plan_type='standard',
            amount=Decimal('200.00'),
            currency='KSH'
        )
        
        expected = f"{self.user.username} - active - 200.00 KSH"
        self.assertEqual(str(subscription), expected)
        print("✓ Subscription string representation works")


class SubscriptionLifecycleTest(TestCase):
    """Test complete subscription lifecycle"""
    
    def setUp(self):
        """Set up test user"""
        self.user = User.objects.create_user(
            username='lifecycleuser',
            email='lifecycle@gmail.com',
            password='pass123'
        )
    
    def test_complete_subscription_lifecycle(self):
        """Test full lifecycle: pending -> active -> expired"""
        # 1. Create pending subscription
        subscription = Subscription.objects.create(
            user=self.user,
            status='pending',
            payment_method='mpesa',
            plan_type='standard',
            amount=Decimal('200.00'),
            currency='KSH',
            mpesa_number='254712345678',
            mpesa_transaction_id='TEST123'
        )
        
        self.assertEqual(subscription.status, 'pending')
        self.assertFalse(subscription.is_active())
        print("✓ Step 1: Subscription created as pending")
        
        # 2. Activate subscription
        subscription.activate(duration_days=30)
        subscription.refresh_from_db()
        
        self.assertEqual(subscription.status, 'active')
        self.assertTrue(subscription.is_active())
        print("✓ Step 2: Subscription activated")
        
        # 3. Simulate expiration by setting end_date to past
        subscription.end_date = timezone.now() - timedelta(days=1)
        subscription.save()
        
        # 4. Check expiration
        is_active = subscription.is_active()
        subscription.refresh_from_db()
        
        self.assertFalse(is_active)
        self.assertEqual(subscription.status, 'expired')
        print("✓ Step 3: Subscription expired automatically")
    
    def test_resubscription_after_expiry(self):
        """Test user can create new subscription after expiry"""
        # Create and expire first subscription
        old_subscription = Subscription.objects.create(
            user=self.user,
            status='active',
            plan_type='standard',
            amount=Decimal('200.00'),
            currency='KSH',
            start_date=timezone.now() - timedelta(days=31),
            end_date=timezone.now() - timedelta(days=1)
        )
        old_subscription.is_active()  # Triggers auto-expiration
        old_subscription.refresh_from_db()
        
        self.assertEqual(old_subscription.status, 'expired')
        
        # Create new subscription
        new_subscription = Subscription.objects.create(
            user=self.user,
            status='pending',
            plan_type='standard',
            amount=Decimal('200.00'),
            currency='KSH'
        )
        new_subscription.activate(duration_days=30)
        
        # Verify new subscription is active
        self.assertTrue(new_subscription.is_active())
        self.assertEqual(new_subscription.status, 'active')
        
        # Verify user has 2 subscriptions (1 expired, 1 active)
        user_subscriptions = Subscription.objects.filter(user=self.user)
        self.assertEqual(user_subscriptions.count(), 2)
        print("✓ User can resubscribe after expiration")


class BillingUsageTest(TestCase):
    """Test BillingUsage model functionality"""
    
    def setUp(self):
        """Set up test user"""
        self.user = User.objects.create_user(
            username='billinguser',
            email='billing@gmail.com',
            password='pass123'
        )
    
    def test_create_billing_usage(self):
        """Test creating billing usage record"""
        billing = BillingUsage.objects.create(
            user=self.user,
            total_predictions=10,
            unique_teams_count=8,
            unique_leagues_count=3,
            is_active=True
        )
        
        self.assertEqual(billing.user, self.user)
        self.assertEqual(billing.total_predictions, 10)
        self.assertTrue(billing.is_active)
        print("✓ Billing usage record created")
    
    def test_billing_usage_for_session(self):
        """Test billing usage with session key"""
        billing = BillingUsage.objects.create(
            session_key='test_session_123',
            total_predictions=5,
            unique_teams_count=4,
            unique_leagues_count=2,
            is_active=True
        )
        
        self.assertIsNone(billing.user)
        self.assertEqual(billing.session_key, 'test_session_123')
        print("✓ Billing usage for anonymous session works")


class SubscriptionPaymentTest(TestCase):
    """Test subscription payment scenarios"""
    
    def setUp(self):
        """Set up test user"""
        self.user = User.objects.create_user(
            username='paymentuser',
            email='payment@gmail.com',
            password='pass123'
        )
    
    def test_mpesa_payment_fields(self):
        """Test M-Pesa payment fields are stored"""
        subscription = Subscription.objects.create(
            user=self.user,
            status='active',
            payment_method='mpesa',
            plan_type='standard',
            amount=Decimal('200.00'),
            currency='KSH',
            mpesa_number='254712345678',
            mpesa_transaction_id='MPESA123XYZ'
        )
        
        self.assertEqual(subscription.mpesa_number, '254712345678')
        self.assertEqual(subscription.mpesa_transaction_id, 'MPESA123XYZ')
        print("✓ M-Pesa payment details stored")
    
    def test_different_currencies(self):
        """Test subscriptions with different currencies"""
        ksh_subscription = Subscription.objects.create(
            user=self.user,
            plan_type='standard',
            amount=Decimal('200.00'),
            currency='KSH'
        )
        
        usd_subscription = Subscription.objects.create(
            user=self.user,
            plan_type='standard',
            amount=Decimal('2.00'),
            currency='USD'
        )
        
        self.assertEqual(ksh_subscription.currency, 'KSH')
        self.assertEqual(usd_subscription.currency, 'USD')
        print("✓ Multiple currencies supported")


class SubscriptionAccessControlTest(TestCase):
    """Test subscription-based access control"""
    
    def setUp(self):
        """Set up test user"""
        self.user = User.objects.create_user(
            username='accessuser',
            email='access@gmail.com',
            password='pass123'
        )
    
    def test_user_with_active_subscription_has_access(self):
        """Test user with active subscription can access"""
        subscription = Subscription.objects.create(
            user=self.user,
            status='active',
            plan_type='standard',
            amount=Decimal('200.00'),
            currency='KSH',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=20)
        )
        
        # User should have access
        active_subscription = Subscription.objects.filter(
            user=self.user,
            status='active'
        ).first()
        
        self.assertIsNotNone(active_subscription)
        self.assertTrue(active_subscription.is_active())
        print("✓ User with active subscription has access")
    
    def test_user_with_expired_subscription_no_access(self):
        """Test user with expired subscription cannot access"""
        subscription = Subscription.objects.create(
            user=self.user,
            status='active',
            plan_type='standard',
            amount=Decimal('200.00'),
            currency='KSH',
            start_date=timezone.now() - timedelta(days=31),
            end_date=timezone.now() - timedelta(days=1)
        )
        
        # Trigger expiration check
        subscription.is_active()
        subscription.refresh_from_db()
        
        # User should not have access
        active_subscription = Subscription.objects.filter(
            user=self.user,
            status='active'
        ).first()
        
        self.assertIsNone(active_subscription)
        self.assertEqual(subscription.status, 'expired')
        print("✓ User with expired subscription blocked")
    
    def test_user_without_subscription_no_access(self):
        """Test user without subscription cannot access"""
        # User has no subscriptions
        active_subscription = Subscription.objects.filter(
            user=self.user,
            status='active'
        ).first()
        
        self.assertIsNone(active_subscription)
        print("✓ User without subscription blocked")


# Test runner configuration
if __name__ == '__main__':
    import unittest
    unittest.main()
