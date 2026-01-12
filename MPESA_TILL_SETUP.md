# M-Pesa Till Number Integration Guide

## Overview
Your Football Prediction App is now configured to use **Till Number 3040653** for M-Pesa payments.

## What Changed

### 1. **Transaction Type**
- **Before**: `CustomerPayBillOnline` (for Paybill numbers)
- **After**: `CustomerBuyGoodsOnline` (for Till numbers)

### 2. **Shortcode Configuration**
- **Till Number**: `3040653`
- **Location**: `settings.py` and `auth_views.py`

## Key Differences: Till Number vs Paybill

| Feature | Till Number | Paybill |
|---------|------------|---------|
| Transaction Type | `CustomerBuyGoodsOnline` | `CustomerPayBillOnline` |
| Use Case | Buy Goods/Services | Bill Payments |
| Account Reference | Optional | Required |
| Password Generation | Shortcode + Passkey + Timestamp | Same |

## Configuration Steps

### Step 1: Get M-Pesa API Credentials

You need to obtain these from the [Safaricom Daraja Portal](https://developer.safaricom.co.ke/):

1. **Consumer Key** - Your API consumer key
2. **Consumer Secret** - Your API consumer secret
3. **Passkey** - Your Lipa Na M-Pesa Online Passkey
4. **Till Number** - `3040653` (already configured)

### Step 2: Set Environment Variables

Add these to your `.env` file (or Render environment variables):

```bash
# M-Pesa Configuration
MPESA_CONSUMER_KEY=your_actual_consumer_key_here
MPESA_CONSUMER_SECRET=your_actual_consumer_secret_here
MPESA_SHORTCODE=3040653
MPESA_PASSKEY=your_actual_passkey_here
MPESA_ENVIRONMENT=production  # Use 'sandbox' for testing
```

### Step 3: Whitelist Callback URL

In the Safaricom Daraja Portal, register your callback URL:

```
https://leon-football.com/api/mpesa/callback/
```

**Important M-Pesa Callback IPs to Whitelist:**
```
196.201.214.200
196.201.214.206
196.201.213.114
196.201.214.207
196.201.214.208
196.201.213.44
196.201.212.127
196.201.212.128
196.201.212.129
196.201.212.136
196.201.212.74
196.201.212.69
```

## Testing the Integration

### Sandbox Testing (Development)

1. Set `MPESA_ENVIRONMENT=sandbox`
2. Use Safaricom sandbox credentials
3. Test with sandbox phone numbers

### Production Testing

1. Set `MPESA_ENVIRONMENT=production`
2. Use your live Till Number credentials
3. Test with a real M-Pesa number (small amount first!)

## Payment Flow

1. **User initiates payment** → Clicks subscribe button
2. **App validates** → Checks phone number format
3. **STK Push sent** → M-Pesa prompt appears on user's phone
4. **User enters PIN** → Completes payment on phone
5. **Callback received** → M-Pesa sends result to your server
6. **Subscription activated** → User gets access immediately

## Code Changes Made

### 1. `predictor/auth_views.py` (Line 490)
```python
# Changed transaction type for Till Number
"TransactionType": "CustomerBuyGoodsOnline",  # Was: CustomerPayBillOnline
```

### 2. `football_predictor/settings.py` (Line 255)
```python
# Updated default shortcode to Till Number
MPESA_SHORTCODE = os.environ.get('MPESA_SHORTCODE', '3040653')
```

### 3. `env.example` (Line 42)
```bash
# Updated example configuration
MPESA_SHORTCODE=3040653  # Till Number
```

## Troubleshooting

### Issue: "Payment initiation failed"
**Solution**: Check that all M-Pesa credentials are correctly set in environment variables

### Issue: "Invalid M-Pesa number format"
**Solution**: Ensure phone number is in format `254XXXXXXXXX` (12 digits)

### Issue: "Callback not received"
**Solution**: 
- Verify callback URL is whitelisted in Daraja Portal
- Check that all M-Pesa IPs are whitelisted in your firewall
- Ensure your server is accessible from the internet

### Issue: "Authentication failed"
**Solution**: 
- Verify Consumer Key and Secret are correct
- Check that credentials match the environment (sandbox vs production)
- Ensure no extra spaces in environment variables

## Security Checklist

- ✅ M-Pesa callback IPs whitelisted
- ✅ CSRF protection enabled
- ✅ HTTPS enforced in production
- ✅ Callback URL registered with Safaricom
- ✅ Transaction logging enabled
- ✅ IP validation on callbacks

## Next Steps

1. **Get your M-Pesa API credentials** from Safaricom Daraja Portal
2. **Add credentials to environment variables** (Render dashboard or `.env` file)
3. **Test in sandbox mode** first
4. **Switch to production** when ready
5. **Monitor transactions** in the admin panel

## Support Resources

- [Safaricom Daraja Portal](https://developer.safaricom.co.ke/)
- [M-Pesa API Documentation](https://developer.safaricom.co.ke/Documentation)
- [Lipa Na M-Pesa Online API](https://developer.safaricom.co.ke/APIs/MpesaExpressSimulate)

## Important Notes

⚠️ **Never commit your `.env` file** to version control
⚠️ **Always test in sandbox** before going live
⚠️ **Monitor callback logs** for debugging
⚠️ **Keep credentials secure** - use environment variables only

---

**Last Updated**: January 12, 2026
**Till Number**: 3040653
**Transaction Type**: CustomerBuyGoodsOnline
