# How to Enable Email Signup in Supabase

## Quick Fix for 403 Forbidden Error

The 403 error means email signup is disabled. Follow these steps:

### Step 1: Enable Email Provider

1. Go to: https://supabase.com/dashboard/project/hdvwwhsiqbtrttzvzyrj
2. Click **Authentication** in the left sidebar
3. Click **Providers** tab
4. Find **Email** in the list
5. Toggle it to **ON** (Enabled)
6. Click **Save**

### Step 2: Enable Email Signup

1. Still in **Authentication** → **Providers**
2. Click on the **Email** provider (or click the settings icon)
3. Make sure these settings are enabled:
   - ✅ **Enable email signup** - TURN ON
   - ✅ **Confirm email** - You can turn this OFF for easier testing, or leave it ON

### Step 3: (Optional) Disable Email Confirmation

If you want users to sign up without email confirmation:

1. Go to **Authentication** → **Settings**
2. Scroll to **Email Auth** section
3. Find **Enable email confirmations**
4. Toggle it to **OFF**
5. Click **Save**

### Step 4: Test Signup

1. Go back to your dashboard: http://localhost:8501
2. Try signing up with: `yourname@buyhatke.com`
3. It should work now!

## If Still Not Working

### Check Site URL Settings

1. Go to **Authentication** → **URL Configuration**
2. Make sure **Site URL** is set (can be any valid URL, e.g., `http://localhost:8501`)
3. Add to **Redirect URLs** if needed: `http://localhost:8501`

### Verify API Key

1. Go to **Settings** → **API**
2. Make sure you're using the **anon/public** key (not the service_role key)
3. The key should start with `eyJ...`

## Table Column Names

Your table shows lowercase columns (shortcode, ownerusername), but the code uses camelCase (shortCode, ownerUsername). This is fine - Supabase automatically handles the conversion. The table structure looks correct!

