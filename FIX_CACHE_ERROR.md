# How to Fix "relation cache_table does not exist"

Your logs show the application is working correctly and serving predictions on `leon-football.com`! 🎉

However, there is one small warning:
`WARNING:predictor.views:Cache clear failed ... relation "cache_table" does not exist`

This happens because the database cache table hasn't been created in your new `football_pro` database yet.

## Solution

1. Go to your **Render Dashboard**.
2. Click on your **Web Service** (`football-predictor`).
3. Click on the **Shell** tab (on the left side).
4. When the terminal loads, paste and run this command:

```bash
python manage.py createcachetable
```

5. You should see `Cache table 'cache_table' created.`

Once this is done, the warning will disappear, and your application performance will improve!
