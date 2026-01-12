#!/bin/bash
# M-Pesa Till Number Configuration
# Copy these to your Render environment variables or .env file

# ============================================
# REQUIRED M-PESA CREDENTIALS
# ============================================

# Get these from: https://developer.safaricom.co.ke/
MPESA_CONSUMER_KEY=your_consumer_key_from_daraja_portal
MPESA_CONSUMER_SECRET=your_consumer_secret_from_daraja_portal
MPESA_SHORTCODE=3040653
MPESA_PASSKEY=your_passkey_from_daraja_portal

# Environment: 'sandbox' for testing, 'production' for live
MPESA_ENVIRONMENT=production

# ============================================
# CALLBACK CONFIGURATION
# ============================================

# Your callback URL (already configured in code):
# https://leon-football.com/api/mpesa/callback/

# Register this URL in Safaricom Daraja Portal under:
# "Lipa Na M-Pesa Online" → "Register URLs"

# ============================================
# IP WHITELIST (Add to your firewall/Render)
# ============================================

# Safaricom M-Pesa Callback IPs:
# 196.201.214.200
# 196.201.214.206
# 196.201.213.114
# 196.201.214.207
# 196.201.214.208
# 196.201.213.44
# 196.201.212.127
# 196.201.212.128
# 196.201.212.129
# 196.201.212.136
# 196.201.212.74
# 196.201.212.69

# ============================================
# QUICK TEST
# ============================================

# 1. Set environment to sandbox first
# 2. Use Safaricom test credentials
# 3. Test with test phone number: 254708374149
# 4. Once working, switch to production

# ============================================
# DEPLOYMENT CHECKLIST
# ============================================

# [ ] Got Consumer Key from Daraja Portal
# [ ] Got Consumer Secret from Daraja Portal
# [ ] Got Passkey from Daraja Portal
# [ ] Added all credentials to Render environment variables
# [ ] Registered callback URL in Daraja Portal
# [ ] Whitelisted M-Pesa IPs in firewall
# [ ] Tested in sandbox mode
# [ ] Switched to production mode
# [ ] Tested with real payment (small amount)
# [ ] Monitoring logs for callbacks

echo "M-Pesa Till Number: 3040653"
echo "Transaction Type: CustomerBuyGoodsOnline"
echo "Callback URL: https://leon-football.com/api/mpesa/callback/"
