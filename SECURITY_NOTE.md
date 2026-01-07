# Security Alert: Automated Bot Traffic Detected 🛡️

The logs you checked show something interesting:

```
[GET] /wp-admin/setup-config.php ... 404 Not Found
[GET] /wordpress/wp-admin/... ... 404 Not Found
```

### What is this?
These are **automative bots** scanning the internet for vulnerable WordPress sites. Since your site (`leon-football.com`) is now live on the public internet, these bots found it and are trying to see if it's a hacked WordPress site.

### Is this a problem?
**NO.** Your site is built with **Django**, not WordPress.
*   The bots are looking for `wp-admin` (WordPress Admin).
*   Your app correctly responds with `404 Not Found`.
*   This proves your security is working! Use of `DEBUG=False` in production hides sensitive error details from them.

### Action Item
**Do nothing.** This is normal "background noise" of the internet. Your application is safe and correctly rejecting these invalid requests.
