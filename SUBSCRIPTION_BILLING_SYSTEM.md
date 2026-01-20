# Subscription Billing System - Documentation

## 📋 **Overview**

The Football Prediction App uses a **monthly subscription billing model** with automatic expiration tracking.

---

## 💳 **Subscription Plans**

### **Available Plans:**

1. **Standard Plan** (KES 200 / $2 USD)
   - Daily Limit: 7 predictions/day
   - Monthly Limit: 300 predictions/month
   - Duration: 30 days

2. **Starter Plan** (KES 500 / $5 USD)
   - Daily Limit: 20 predictions/day
   - Monthly Limit: 600 predictions/month
   - Duration: 30 days

3. **VIP Plan** (KES 1000 / $10 USD)
   - Daily Limit: 100 predictions/day
   - Monthly Limit: 1500 predictions/month
   - Duration: 30 days

---

## ⏰ **Subscription Lifecycle**

### **1. New Subscription**
- User initiates payment via M-Pesa/PayPal
- Status: `pending`
- No start_date or end_date yet

### **2. Payment Confirmed**
- Status changes to: `active`
- `start_date` = Current date/time
- `end_date` = start_date + 30 days
- User can now make predictions

### **3. Active Subscription**
- User has full access to predictions
- System tracks daily and monthly usage
- Days remaining countdown

### **4. Subscription Expires**
- When `current_date > end_date`:
  - Status automatically changes to: `expired`
  - User loses access to predictions
  - **User must resubscribe to continue**

### **5. Cancelled Subscription**
- User or admin cancels subscription
- Status: `cancelled`
- Access revoked immediately

---

## 🔄 **Automatic Expiration Logic**

### **How It Works:**

The system automatically checks subscription status using the `is_active()` method:

```python
def is_active(self):
    """Check if subscription is currently active."""
    if self.status != 'active':
        return False
    if self.end_date and timezone.now() > self.end_date:
        self.status = 'expired'  # Auto-expire
        self.save()
        return False
    return True
```

**This means:**
- ✅ Every time a user tries to make a prediction, the system checks if their subscription is still valid
- ✅ If the end_date has passed, the subscription is automatically marked as `expired`
- ✅ User is blocked from making predictions
- ✅ **User MUST subscribe again to continue**

---

## 🔔 **User Notifications**

### **When Subscription Expires:**

Users are notified in several ways:

1. **Dashboard Message:**
   - "Your subscription has expired. Please renew to continue making predictions."

2. **Prediction Page:**
   - Blocked with message: "Subscription expired. Subscribe now to access predictions."

3. **Email Notification:** (Optional - can be implemented)
   - Sent 3 days before expiration
   - Sent on expiration day
   - Reminder after 7 days

---

## 📊 **Subscription Status Types**

| Status | Description | User Access | Action Required |
|--------|-------------|-------------|-----------------|
| **Pending** | Payment initiated but not confirmed | ❌ No access | Wait for payment confirmation |
| **Active** | Subscription is valid and current | ✅ Full access | None - enjoy predictions! |
| **Expired** | Subscription term ended | ❌ No access | **Resubscribe to continue** |
| **Cancelled** | User or admin cancelled | ❌ No access | Resubscribe if desired |

---

## 💡 **Resubscription Process**

### **When a subscription expires, users must:**

1. **Go to Subscription Page**
   - Click "Subscribe" or "Renew Subscription"

2. **Select Plan**
   - Choose: Standard, Starter, or VIP

3. **Make Payment**
   - M-Pesa STK Push
   - PayPal (if configured)

4. **Payment Confirmed**
   - New subscription created
   - Status: `active`
   - New 30-day period starts

### **Important Notes:**
- ❌ **No automatic renewal** - Users must manually resubscribe
- ❌ **No grace period** - Access stops immediately when subscription expires
- ✅ **Can resubscribe anytime** - Even after months of inactivity
- ✅ **Previous predictions are preserved** - History is not deleted

---

## 🛠️ **Admin Features**

### **Subscription Management:**

Admins can:
1. **View all subscriptions** - Active, expired, pending, cancelled
2. **Manually activate** - Bypass payment for testing or special cases
3. **Extend subscriptions** - Add 30 days to existing subscription
4. **Cancel subscriptions** - Revoke access immediately
5. **View expiration dates** - See when subscriptions will expire

### **Admin Actions:**
- ✓ Activate selected subscriptions
- ✗ Cancel selected subscriptions
- ⏰ Extend by 30 days

---

## 📈 **Billing Analytics**

### **Tracked Metrics:**
- Total active subscriptions
- Total revenue (active subscriptions only)
- Expired subscriptions count
- Pending payments count
- Revenue trend (30 days)
- Subscription by plan type

---

## 🔐 **Security & Validation**

### **Payment Verification:**
- M-Pesa transaction IDs are stored and verified
- Duplicate payments are prevented
- Failed payments don't activate subscriptions

### **Access Control:**
- Every prediction request checks subscription status
- Expired subscriptions are auto-detected
- Users cannot bypass expiration

---

## 📝 **Database Schema**

### **Subscription Model Fields:**

```python
user                    # ForeignKey to User
status                  # active/expired/cancelled/pending
payment_method          # mpesa/paypal/stripe
plan_type              # standard/starter/vip
amount                 # Decimal (200.00, 500.00, 1000.00)
currency               # KSH or USD
mpesa_number           # Phone number for M-Pesa
mpesa_transaction_id   # Transaction reference
start_date             # When subscription became active
end_date               # When subscription expires (start_date + 30 days)
created_at             # When subscription was created
updated_at             # Last modification
```

---

## ✅ **Current Implementation Status**

- ✅ Monthly billing (30-day subscriptions)
- ✅ Automatic expiration detection
- ✅ Multiple plan types (Standard, Starter, VIP)
- ✅ M-Pesa payment integration
- ✅ Admin management interface
- ✅ Subscription status tracking
- ✅ Daily and monthly limits
- ⚠️ **Email notifications** - Not yet implemented
- ⚠️ **Automatic renewal** - Not implemented (by design)

---

## 🚀 **Recommended Improvements**

### **1. Email Notifications:**
Send emails to users:
- 7 days before expiration: "Your subscription expires in 7 days"
- 3 days before expiration: "Your subscription expires in 3 days"
- On expiration day: "Your subscription has expired. Renew now!"
- 7 days after expiration: "We miss you! Resubscribe to continue"

### **2. Grace Period (Optional):**
- Allow 3-day grace period after expiration
- User can still access with warning message
- Encourages immediate renewal

### **3. Auto-Renewal (Optional):**
- Allow users to opt-in for automatic renewal
- Charge M-Pesa automatically when subscription expires
- Requires stored payment method

### **4. Subscription History:**
- Show users their past subscriptions
- Display total amount spent
- Show subscription streak (consecutive months)

---

## 📞 **User Support**

### **Common Questions:**

**Q: What happens when my subscription expires?**
A: You lose access to predictions immediately. You must resubscribe to continue.

**Q: Do I get a refund if I cancel early?**
A: No, subscriptions are non-refundable. You keep access until the end date.

**Q: Can I upgrade my plan mid-subscription?**
A: Yes, contact admin or purchase a new subscription (current one will be cancelled).

**Q: Is there automatic renewal?**
A: No, you must manually resubscribe each month.

**Q: What happens to my prediction history?**
A: Your history is preserved forever, even after subscription expires.

---

## 🎯 **Summary**

**YES, when a subscription expires (end_date < current_date):**
1. ✅ Status automatically changes to `expired`
2. ✅ User loses access to predictions
3. ✅ User sees notification to resubscribe
4. ✅ **User MUST subscribe again** to continue
5. ✅ No automatic renewal - manual resubscription required

**The system is designed to:**
- Automatically detect expired subscriptions
- Block access when expired
- Prompt users to resubscribe
- Make resubscription easy and quick
