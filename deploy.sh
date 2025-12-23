#!/bin/bash
# Production deployment script for Football Predictor Pro

set -e

echo "🚀 Starting production deployment..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  Warning: .env file not found. Using defaults."
fi

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --settings=football_predictor.settings_production

# Run database migrations
echo "🗄️  Running database migrations..."
python manage.py migrate --settings=football_predictor.settings_production

# Create superuser (if needed)
# python manage.py createsuperuser --noinput --settings=football_predictor.settings_production

# Check database connection
echo "🔍 Checking database connection..."
python manage.py check --database default --settings=football_predictor.settings_production

# Validate settings
echo "✅ Validating production settings..."
python manage.py check --deploy --settings=football_predictor.settings_production

echo "✨ Deployment preparation complete!"
echo "📝 Next steps:"
echo "   1. Start services: docker-compose -f docker-compose.prod.yml up -d"
echo "   2. Check logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   3. Monitor health: curl http://localhost:8000/health/"

