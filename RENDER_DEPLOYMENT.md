# Deploying Football Predictor Pro to Render

This guide will help you deploy the Football Predictor Pro application to Render.

## Prerequisites

1. A Render account (sign up at https://render.com)
2. Your code pushed to a Git repository (GitHub, GitLab, or Bitbucket)

## Step-by-Step Deployment

### Option 1: Using render.yaml (Recommended)

1. **Push your code to Git**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Create a new Web Service on Render**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your Git repository
   - Render will automatically detect `render.yaml`

3. **Configure Environment Variables**
   In the Render dashboard, add these environment variables:
   ```
   SECRET_KEY=<generate a strong secret key>
   DEBUG=False
   ALLOWED_HOSTS=your-app-name.onrender.com
   ```
   
   To generate a SECRET_KEY:
   ```python
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

4. **Add PostgreSQL Database (Optional but Recommended)**
   - Go to "New +" → "PostgreSQL"
   - Create a new database
   - Copy the "Internal Database URL"
   - Add it as `DATABASE_URL` environment variable in your web service

5. **Add Redis (Optional)**
   - Go to "New +" → "Redis"
   - Create a new Redis instance
   - Copy the "Internal Redis URL"
   - Add it as `REDIS_URL` environment variable in your web service

6. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your app

### Option 2: Manual Configuration

1. **Create a new Web Service**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your Git repository

2. **Configure Build Settings**
   - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command:** `gunicorn football_predictor.wsgi:application`

3. **Set Environment Variables**
   ```
   PYTHON_VERSION=3.11.0
   SECRET_KEY=<your-secret-key>
   DEBUG=False
   ALLOWED_HOSTS=your-app-name.onrender.com
   DATABASE_URL=<from-postgres-service>
   REDIS_URL=<from-redis-service> (optional)
   ```

4. **Deploy**

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `SECRET_KEY` | Yes | Django secret key | Generated key |
| `DEBUG` | Yes | Debug mode | `False` |
| `ALLOWED_HOSTS` | Yes | Allowed hostnames | `your-app.onrender.com` |
| `DATABASE_URL` | No | PostgreSQL connection URL | Auto-set by Render PostgreSQL |
| `REDIS_URL` | No | Redis connection URL | Auto-set by Render Redis |

## Post-Deployment Steps

1. **Create a Superuser**
   - Go to Render dashboard → Shell
   - Run: `python manage.py createsuperuser`

2. **Load Initial Data (if needed)**
   ```bash
   python manage.py populate_leagues_teams
   ```

3. **Verify Deployment**
   - Visit your app URL: `https://your-app-name.onrender.com`
   - Check admin panel: `https://your-app-name.onrender.com/admin`

## Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Ensure all dependencies are in `requirements.txt`
- Verify Python version compatibility

### Static Files Not Loading
- Ensure `collectstatic` runs during build
- Check `STATIC_ROOT` and `STATIC_URL` settings
- Verify WhiteNoise is installed and configured

### Database Connection Issues
- Verify `DATABASE_URL` is set correctly
- Check PostgreSQL service is running
- Ensure `psycopg2-binary` is in requirements.txt

### Application Crashes
- Check application logs in Render dashboard
- Verify all environment variables are set
- Check `ALLOWED_HOSTS` includes your Render domain

## Performance Optimization

1. **Upgrade Plan**: Start with "Starter" plan, upgrade to "Standard" or "Pro" for production
2. **Enable Redis**: Improves caching and session management
3. **Database Connection Pooling**: Already configured in settings
4. **CDN**: Consider using Cloudflare for static assets

## Monitoring

- View logs in Render dashboard
- Set up health checks (already configured)
- Monitor database and Redis usage

## Security Checklist

- ✅ SECRET_KEY is set via environment variable
- ✅ DEBUG is set to False
- ✅ ALLOWED_HOSTS is configured
- ✅ Database credentials are secure
- ✅ Static files are served securely via WhiteNoise

## Support

For issues specific to Render, check:
- Render Documentation: https://render.com/docs
- Render Community: https://community.render.com

For application-specific issues, check the project's README.md

