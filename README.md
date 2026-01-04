# Football Predictor Web App

A professional Django-based football prediction platform with integrated M-Pesa payments and advanced analytics.

## Features
- **Accurate Predictions**: Uses Dual-Model analysis (Model 1 & Model 2).
- **M-Pesa Integration**: Automated subscription payments via Safaricom Daraja API (STK Push).
- **User Dashboard**: Track prediction history and subscription status.
- **Admin Panel**: Manage users, subscriptions, and view analytics.
- **Responsive Design**: Professional UI with dark/light mode aesthetics.

## Local Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/Bushmark-tech/FOOTBALL.git
   cd FOOTBALL
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```
4. **Start Server**:
   ```bash
   python manage.py runserver
   ```

## M-Pesa Configuration (Production)
Set the following Environment Variables in your deployment dashboard (e.g., Render):
- `MPESA_CONSUMER_KEY`
- `MPESA_CONSUMER_SECRET`
- `MPESA_PASSKEY`
- `MPESA_SHORTCODE` (Paybill/Till Number)
- `MPESA_ENVIRONMENT` (Set to 'production')

## Deployment
This project is configured for **Render**.
1. Connect your GitHub repository to Render.
2. Select "Web Service".
3. Use the following build command:
   ```bash
   ./build.sh
   ```
4. Start command:
   ```bash
   gunicorn football_predictor.wsgi:application
   ```

## License
© 2026 Bushmark Tech. All Rights Reserved.
