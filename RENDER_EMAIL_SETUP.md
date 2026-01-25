# How to Configure Email on Render

Since your code is already pushed to GitHub (`git push`), you just need to update your **Environment Variables** in the Render Dashboard. Use the exact same credentials we verified locally.

## Step 1: Go to Render Dashboard
1. Log in to [dashboard.render.com](https://dashboard.render.com).
2. Click on your web service (e.g., `football-predictor`).
3. Click on **"Environment"** in the left sidebar.

## Step 2: Add These Variables
You need to add the following Key-Value pairs. Scroll down to "Environment Variables" and click **"Add Environment Variable"** for each one:

| Key | Value |
| --- | --- |
| `EMAIL_BACKEND` | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST` | `smtp.gmail.com` |
| `EMAIL_PORT` | `587` |
| `EMAIL_USE_TLS` | `True` |
| `EMAIL_HOST_USER` | `wasikeonesmus980@gmail.com` |
| `EMAIL_HOST_PASSWORD` | `bvio ckzt olvm ovjl` |
| `DEFAULT_FROM_EMAIL` | `Football Predictor <noreply@football-predictor.com>` |
| `SITE_URL` | `https://football-o48u.onrender.com` |

> **Note:** The `EMAIL_HOST_PASSWORD` is the same 16-character App Password we generated earlier. Do **NOT** use your normal Gmail password.

## Step 3: Save Changes
1. Click **"Save Changes"** at the bottom.
2. Render will automatically redeploy your application to apply these new settings.

## Step 4: Verify
Once the deployment finishes (usually 2-3 minutes):
1. Go to your live site (`https://football-o48u.onrender.com`).
2. Try the "Forgot Password" link.
3. You should receive the email in your inbox!
