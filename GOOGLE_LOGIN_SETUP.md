# How to Get Google API Keys for Login

Follow these exact steps to get your `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.

### Step 1: Go to Google Cloud Console
1. Open this link in your browser: **[https://console.cloud.google.com/](https://console.cloud.google.com/)**
2. Sign in with your Google (Gmail) account.

### Step 2: Create a New Project
1. In the top-left corner (next to the "Google Cloud" logo), click the **Select a project** dropdown.
2. Click **New Project** in the top-right of the popup.
3. **Project Name**: Enter `Football App` (or any name you like).
4. Click **Create**.
5. Wait a moment, then click **Select Project** in the notification that appears.

### Step 3: Configure Consent Screen
1. In the left sidebar menu (click the ☰ icon if needed), go to **APIs & Services** > **OAuth consent screen**.
2. Select **External** (this allows any Google user to log in).
3. Click **Create**.
4. **App Information**:
   - **App name**: `Football Predictor`
   - **User support email**: Select your email address.
5. **Developer Contact Information**:
   - **Email addresses**: Enter your email address again.
6. Click **Save and Continue** (you can skip the "Scopes" step by clicking Save and Continue again).
7. On the **Test Users** step, click **Add Users** and enter your own email address (this allows you to test it before "publishing").
8. Click **Save and Continue**.

### Step 4: Create Credentials (The Keys)
1. In the left sidebar, click **Credentials**.
2. Click **+ CREATE CREDENTIALS** at the top and select **OAuth client ID**.
3. **Application type**: Select **Web application**.
4. **Name**: `Django Client` (default is fine).
5. **Authorized JavaScript origins**:
   - Click **ADD URI**.
   - Enter: `http://127.0.0.1:8000`
   - Click **ADD URI** again.
   - Enter: `http://localhost:8000`
6. **Authorized redirect URIs** (Crucial Step):
   - Click **ADD URI**.
   - Enter: `http://127.0.0.1:8000/accounts/google/login/callback/`
   - Click **ADD URI** again.
   - Enter: `http://localhost:8000/accounts/google/login/callback/`
7. Click **Create**.

### Step 5: Copy Your Keys
A popup will appear with your keys.
1. Copy **Your Client ID**.
2. Copy **Your Client Secret**.

### Step 6: Add to Your Project
1. Open the file called `.env` in this folder.
2. Find the lines that look like this:
   ```
   GOOGLE_CLIENT_ID=
   GOOGLE_CLIENT_SECRET=
   ```
3. Paste your keys after the equals sign. For example:
   ```
   GOOGLE_CLIENT_ID=123456789-abcdefg.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=GOCSPX-AbCdEfGhIjKlMnOpQrStUvWxYz
   ```
4. Save the file.
5. **Restart your server** (Stopping it and starting it again) for the changes to take effect.

Once you have done this, ask me to "Restore the Google Login button" and I will bring it back!
