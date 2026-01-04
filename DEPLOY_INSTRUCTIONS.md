# Deploying to Render.com

Your Django application is fully configured for deployment on Render. Since you have an existing PostgreSQL database on Render, follow these steps to link them.

## 1. Push Code to GitHub
Ensure all your latest changes (including `settings.py` and `render.yaml`) are pushed to your GitHub repository.
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

## 2. Create Web Service on Render
1. Go to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** -> **Web Service**.
3. Select your GitHub repository (`Football-main` or similar).
4. Render will detect `render.yaml` and may autocomplete settings. If manual setup is needed:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command**: `gunicorn football_predictor.wsgi:application`

## 3. Configure Environment Variables
This is the most critical step. You must add the following **Environment Variables** in the Render Dashboard (under the **Environment** tab of your Web Service):

| Key | Value | Notes |
|-----|-------|-------|
| `DATABASE_URL` | `postgresql://football_pro_user:dECkrRNA8SJGJdb6MR3r6A1KKE6l87n8@dpg-d5chogv5r7bs73b1m410-a/football_pro` | **Use the Internal URL** from your screenshot if in the same region. |
| `SECRET_KEY` | *(Generate a random string)* | You like `django-insecure-...` for dev, but use a strong random string here. |
| `DEBUG` | `False` | Essential for production security. |
| `PYTHON_VERSION` | `3.11.0` | Or `3.10.11` matching your local environment. |
| `MPESA_CONSUMER_KEY` | *(Your Live Key)* | If verifying payments. |
| `MPESA_CONSUMER_SECRET` | *(Your Live Secret)* | |
| `MPESA_PASSKEY` | *(Your Live Passkey)* | |

**Important:** Do **NOT** put the Database URL in `render.yaml` or `settings.py` directly. Use the Environment Variable method to keep it secure.

## 4. Deploy
- Click **Create Web Service** / **Save Changes**.
- Render will start the build.
- Watch the **Logs** tab. It will install dependencies, run `collectstatic`, and apply database migrations (`python manage.py migrate`).

## 5. Verify
Once the deployment status is **Live**:
- Visit your Render URL (e.g., `https://football-predictor.onrender.com`).
- Log in to `/admin` to verify database connectivity.
