# How to Reset Admin Password (If Login Fails)

If you cannot log in with `admin` / `adminpassword`, do this:

1.  **Open Render Dashboard** -> **Web Service** -> **Shell**.
2.  Run this command:

```bash
python reset_admin_password.py
```

3.  It should say: `✅ Updated user 'admin' with password 'adminpassword'`

Then try logging in again at:
👉 **[https://leon-football.com/admin/](https://leon-football.com/admin/)**

(Note: Your custom dashboard is at `/admin/`, while the detailed Django database admin is at `/system-core-database/`)
