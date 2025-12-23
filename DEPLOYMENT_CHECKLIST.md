# Render Deployment Checklist

## ✅ Pre-Deployment Checklist

### Security Fixes (COMPLETED)
- [x] SECRET_KEY moved to environment variable
- [x] ALLOWED_HOSTS configured via environment variable
- [x] DEBUG set via environment variable
- [x] Database URL configured for Render PostgreSQL
- [x] Redis URL configured for Render Redis (optional)

### Configuration Files (COMPLETED)
- [x] `render.yaml` created
- [x] `Procfile` created
- [x] `build.sh` created
- [x] `requirements.txt` updated with production dependencies
- [x] Settings updated for Render environment

### Dependencies Added
- [x] `gunicorn` - WSGI server
- [x] `whitenoise` - Static file serving
- [x] `dj-database-url` - Database URL parsing
- [x] `psycopg2-binary` - PostgreSQL adapter

## 🚀 Deployment Steps

### 1. Push to Git Repository
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Create Render Account
- Sign up at https://render.com
- Connect your Git repository (GitHub/GitLab/Bitbucket)

### 3. Create Web Service
- Go to Render Dashboard → "New +" → "Web Service"
- Connect your repository
- Render will auto-detect `render.yaml`

### 4. Set Environment Variables
In Render Dashboard → Environment:
```
SECRET_KEY=<generate-strong-key>
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
```

Generate SECRET_KEY:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Add PostgreSQL Database (Recommended)
- "New +" → "PostgreSQL"
- Copy Internal Database URL
- Add as `DATABASE_URL` environment variable (auto-added by Render)

### 6. Add Redis (Optional)
- "New +" → "Redis"
- Copy Internal Redis URL
- Add as `REDIS_URL` environment variable

### 7. Deploy
- Click "Create Web Service"
- Wait for build to complete
- Your app will be live at `https://your-app-name.onrender.com`

## 🔧 Post-Deployment

### Create Superuser
1. Go to Render Dashboard → Shell
2. Run: `python manage.py createsuperuser`

### Load Initial Data (if needed)
```bash
python manage.py populate_leagues_teams
```

### Verify Deployment
- [ ] Homepage loads correctly
- [ ] Static files (CSS/JS) load
- [ ] Database connections work
- [ ] Admin panel accessible
- [ ] Predictions functionality works

## 📝 Important Notes

1. **First Deployment**: May take 5-10 minutes
2. **Free Tier**: Apps sleep after 15 minutes of inactivity
3. **Database**: PostgreSQL is persistent, SQLite is not recommended
4. **Static Files**: Served via WhiteNoise (configured)
5. **Environment**: All sensitive data via environment variables

## 🐛 Troubleshooting

### Build Fails
- Check build logs
- Verify all dependencies in `requirements.txt`
- Check Python version (3.11.0)

### Static Files 404
- Ensure `collectstatic` runs in build
- Check `STATIC_ROOT` setting
- Verify WhiteNoise middleware is active

### Database Errors
- Verify `DATABASE_URL` is set
- Check PostgreSQL service is running
- Run migrations: `python manage.py migrate`

### App Crashes
- Check application logs
- Verify `ALLOWED_HOSTS` includes Render domain
- Check all environment variables are set

## 📚 Documentation

- Full deployment guide: `RENDER_DEPLOYMENT.md`
- Project review: `PROJECT_REVIEW.md`
- Main README: `README.md`

## ✅ Ready to Deploy!

Your project is now configured for Render deployment. Follow the steps above to deploy.

