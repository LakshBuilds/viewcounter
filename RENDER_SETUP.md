# Render Deployment Guide

This guide will help you deploy the Instagram Creators Dashboard to Render.

## Prerequisites

- A Render account (sign up at https://render.com)
- All your API keys ready:
  - Apify API token
  - Supabase URL and anon key
  - Clerk secret key and publishable key

## Step 1: Create a New Web Service

1. Go to your Render dashboard
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Select the repository: `LakshBuilds/viewcounter`

## Step 2: Configure Build Settings

- **Name**: `instagram-creators-dashboard` (or your preferred name)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

## Step 3: Set Environment Variables

In the Render dashboard, go to **Environment** section and add these variables:

### Required Environment Variables

```
APIFY_API_TOKEN=your_apify_api_token_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
CLERK_SECRET_KEY=sk_test_your_clerk_secret_key_here
CLERK_FRONTEND_API=pk_test_your_clerk_publishable_key_here
```

### How to Add Environment Variables in Render

1. In your service settings, scroll to **Environment Variables**
2. Click "Add Environment Variable"
3. Add each variable one by one:
   - **Key**: `APIFY_API_TOKEN`
   - **Value**: Your actual Apify API token
   - Repeat for all variables above

## Step 4: Update Streamlit Configuration

Create a `.streamlit/config.toml` file in your repository (if it doesn't exist):

```toml
[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

## Step 5: Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Start your Streamlit app
3. Your app will be available at: `https://your-service-name.onrender.com`

## Step 6: Configure Custom Domain (Optional)

1. Go to your service settings
2. Click "Custom Domains"
3. Add your domain and follow DNS configuration instructions

## Troubleshooting

### App Not Starting

- Check the logs in Render dashboard
- Ensure all environment variables are set correctly
- Verify the start command includes `--server.port=$PORT --server.address=0.0.0.0`

### Environment Variables Not Working

- Make sure variable names match exactly (case-sensitive)
- Restart the service after adding new environment variables
- Check that values don't have extra spaces or quotes

### Database Connection Issues

- Verify Supabase URL and key are correct
- Check Supabase project settings for allowed IPs (Render IPs should be allowed)
- Ensure your Supabase table schema matches the expected structure

## Render Free Tier Limitations

- Services spin down after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds
- Consider upgrading to paid plan for always-on service

## Security Notes

- Never commit `.env` file to Git
- Use Render's environment variables for all secrets
- Keep your API keys secure and rotate them regularly
- Use Clerk's production keys for production deployments

## Support

If you encounter issues:
1. Check Render service logs
2. Verify all environment variables are set
3. Test locally with the same environment variables
4. Check Streamlit documentation for deployment-specific issues

