# Supabase Setup Instructions

## 1. Create a Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign up or log in
3. Create a new project
4. Wait for the project to be fully provisioned

## 2. Get Your Supabase Credentials

1. In your Supabase project dashboard, go to **Settings** → **API**
2. Copy your **Project URL** (this is your `SUPABASE_URL`)
3. Copy your **anon/public key** (this is your `SUPABASE_KEY`)

## 3. Enable Authentication

1. In your Supabase project, go to **Authentication** → **Providers**
2. Make sure **Email** provider is enabled (it's enabled by default)
3. Optionally configure email templates in **Authentication** → **Email Templates**
4. Go to **Authentication** → **URL Configuration** and set your site URL if needed

**Important**: The dashboard only allows @buyhatke.com business emails for registration and login.

## 4. Create the Database Table

1. In your Supabase project, go to **SQL Editor**
2. Click **New Query**
3. Copy and paste the contents of `supabase_schema.sql`
4. Click **Run** to execute the SQL

This will create the `reels` table with all necessary columns and indexes.

## 5. Configure the Dashboard

1. Open the Streamlit dashboard
2. You'll see a login/signup page
3. **First time**: Click "Sign Up" tab and create an account with your @buyhatke.com email
4. **Admin users**: After login, expand **⚙️ Supabase Configuration (Admin Only)** section
5. Paste your Supabase URL and Key
6. Click outside the input fields to save

**Note**: Only users with @buyhatke.com emails can register. All @buyhatke.com users are admins and can see/change the Apify API key.

## 6. Test the Integration

1. Add a reel URL using the dashboard
2. Check your Supabase dashboard → **Table Editor** → **reels** table
3. You should see the data appear there
4. Refresh the Streamlit page - your data should persist!

## Environment Variables (Optional)

You can also set these as environment variables:

```bash
export SUPABASE_URL="your-project-url"
export SUPABASE_KEY="your-anon-key"
```

Or create a `.env` file:

```
SUPABASE_URL=your-project-url
SUPABASE_KEY=your-anon-key
```

## Features

### Authentication & Security
- ✅ **Email-based Login**: Secure authentication using Supabase Auth
- ✅ **Business Email Only**: Only @buyhatke.com emails can register and login
- ✅ **Admin Access**: All @buyhatke.com users are admins with full access
- ✅ **API Key Protection**: Apify API key is only visible/editable by admins
- ✅ **Session Management**: Secure session handling with logout functionality

### Data Management
- ✅ **Automatic Save**: All reels are automatically saved to Supabase when added
- ✅ **Auto-Load**: Data is automatically loaded from Supabase when you open the dashboard
- ✅ **Refresh Sync**: When you refresh all reels, updates are saved to Supabase
- ✅ **Duplicate Prevention**: The system checks for existing reels before inserting
- ✅ **Update Existing**: If a reel already exists, it updates the record instead of creating a duplicate

## Troubleshooting

- **"Could not load data from Supabase"**: Check that your URL and Key are correct
- **"Error saving to Supabase"**: Make sure the `reels` table exists and RLS policies allow writes
- **Data not persisting**: Verify your Supabase credentials are correct and the table was created successfully

