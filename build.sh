#!/bin/bash
# Build script for Render deployment

set -o errexit  # Exit on error

echo "Starting build process..."

# Install dependencies
echo "Installing Python dependencies..."
# Force install critical dependencies first to bypass cache/resolution issues
pip install PyJWT>=2.8.0 cryptography>=41.0.0 requests-oauthlib>=1.3.0

cat requirements.txt
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running database migrations..."
python manage.py migrate --noinput

# Create cache table if it doesn't exist
echo "Creating cache table..."
python manage.py createcachetable

# Seed database with leagues and teams
echo "Seeding database with leagues and teams..."
python manage.py seed_leagues

echo "Build completed successfully!"

