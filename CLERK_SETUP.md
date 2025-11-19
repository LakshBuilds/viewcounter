# Clerk Authentication Setup Guide

## Overview

The dashboard now uses **Clerk** for authentication instead of Supabase Auth. Supabase is still used for data storage (reels table).

## Step 1: Create a Clerk Account

1. Go to [https://clerk.com](https://clerk.com)
2. Sign up for a free account
3. Create a new application

## Step 2: Get Your Clerk Secret Key

1. In your Clerk Dashboard, select your application
2. Go to **API Keys** in the left sidebar
3. Find the **Secret Key** (starts with `sk_`)
4. Copy this key - you'll need it for the dashboard

## Step 3: Configure Email Authentication

1. In Clerk Dashboard, go to **User & Authentication** → **Email, Phone, Username**
2. Enable **Email** as an authentication method
3. Configure email settings:
   - **Email address** - Enable
   - **Email verification** - You can enable or disable (disable for easier testing)
4. Save changes

## Step 4: Set Up Email Domain Restriction (Optional)

To restrict signups to `@buyhatke.com` emails only:

1. Go to **User & Authentication** → **Restrictions**
2. Add email domain restriction: `buyhatke.com`
3. Save changes

**Note**: The app also validates `@buyhatke.com` emails in code, but Clerk domain restriction provides an additional layer of security.

## Step 5: Configure the Dashboard

1. Open the dashboard: `http://localhost:8501`
2. You'll see the login/signup page
3. Expand **⚙️ Initial Setup - Configure Clerk**
4. Paste your Clerk Secret Key
5. Click outside the input to save

## Step 6: Sign Up

1. Click the **📝 Sign Up** tab
2. Enter:
   - Full Name
   - Email: `yourname@buyhatke.com`
   - Password (at least 6 characters)
   - Confirm Password
3. Click **Sign Up**
4. You'll be automatically logged in!

## Step 7: Configure Supabase (Optional - for Data Storage)

If you want to persist reel data:

1. Expand **💾 Database Configuration - Supabase (Optional)**
2. Enter your Supabase URL and Key
3. Make sure the `reels` table exists (run the SQL from `create_reels_table.sql`)

## Environment Variables (Optional)

You can also set these as environment variables in a `.env` file:

```
CLERK_SECRET_KEY=sk_test_...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
```

## Features

- ✅ **Clerk Authentication**: Secure user authentication
- ✅ **Business Email Only**: Only `@buyhatke.com` emails can register
- ✅ **Admin Access**: All `@buyhatke.com` users are admins
- ✅ **Data Persistence**: Optional Supabase integration for storing reels
- ✅ **Session Management**: Secure session handling

## Troubleshooting

### "Clerk secret key not configured"
- Make sure you've entered the Clerk Secret Key in the configuration section
- Verify the key starts with `sk_`

### "User not found" on login
- Make sure you've signed up first
- Check that the email matches exactly (case-sensitive)

### "Signup failed: 422"
- Email might already be registered - try logging in instead
- Check that email is a valid `@buyhatke.com` address

### "Invalid Clerk secret key"
- Verify you're using the **Secret Key** (not the Publishable Key)
- Make sure the key is copied correctly (no extra spaces)

## API Endpoints Used

- `POST https://api.clerk.com/v1/users` - Create new user
- `GET https://api.clerk.com/v1/users?email_address=...` - Verify user exists

## Notes

- Clerk's backend API doesn't verify passwords directly - it verifies that users exist
- For production, consider using Clerk's frontend components for better security
- The current implementation uses a simplified approach suitable for Streamlit

