# 🚨 Critical Deployment Fix: Database Configuration Error

Your Django deployment is failing with the following error:
`FATAL: database "football" does not exist`

This means your Render Web Service is configured to connect to a PostgreSQL database named `football`, but the actual database on your Render PostgreSQL instance has a different name.

## 🛠️ How to Fix This (Step-by-Step)

You need to update the `DATABASE_URL` environment variable in your Render dashboard to match the *actual* database name.

### Step 1: Find the Correct Database Name and URL
1.  Go to your **Render Dashboard**.
2.  Click on your **PostgreSQL** service (usually named `football-predictor-db` or similar).
3.  Scroll down to the **Connections** section.
4.  Look for **Internal Connection String**.
5.  **Copy** this entire string.
    *   It should look like: `postgres://user:password@hostname:port/database_name`
    *   Check the end of the URL. It is likely **NOT** `.../football`. It might be `.../football_predictor`, `.../football_db`, or a random string.

### Step 2: Update the Web Service Configuration
1.  Go back to the Dashboard and click on your **Web Service** (`football-predictor`).
2.  Click on **Environment** (or "Environment Variables").
3.  Find the `DATABASE_URL` variable.
4.  **Edit** it and paste the **Internal Connection String** you copied in Step 1.
5.  **Save Changes**.

### Step 3: Trigger a Redeploy
1.  After saving, Render usually triggers a new deployment automatically.
2.  If not, click **Manual Deploy** -> **Deploy latest commit**.

---

## ⚠️ Important Note on Database Creation
If you intended for the database to be named `football`, it was not created. Render databases are usually created with a default name unless specified during creation. It is safer to use the default name provided by Render rather than forcing `football`.

Re-copying the **Internal Connection String** is the surest way to fix this.
