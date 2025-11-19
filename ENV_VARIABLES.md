# Environment Variables Configuration

This document lists all required environment variables for the Instagram Creators Dashboard.

## For Local Development

Create a `.env` file in the project root with the following variables:

```env
APIFY_API_TOKEN=your_apify_api_token_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
CLERK_SECRET_KEY=sk_test_your_clerk_secret_key_here
CLERK_FRONTEND_API=pk_test_your_clerk_publishable_key_here
```

## For Render Deployment

Add these environment variables in your Render dashboard under **Environment Variables**:

### Required Variables

| Variable Name | Description | Example |
|--------------|-------------|---------|
| `APIFY_API_TOKEN` | Your Apify API token | `apify_api_xxxxxxxxxxxxx` |
| `SUPABASE_URL` | Your Supabase project URL | `https://xxxxx.supabase.co` |
| `SUPABASE_KEY` | Your Supabase anonymous/public key | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `CLERK_SECRET_KEY` | Your Clerk secret key | `sk_test_xxxxxxxxxxxxx` |
| `CLERK_FRONTEND_API` | Your Clerk publishable key | `pk_test_xxxxxxxxxxxxx` |

### Alternative Variable Names (for compatibility)

The app also supports these alternative variable names:

- `NEXT_PUBLIC_SUPABASE_URL` (instead of `SUPABASE_URL`)
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` or `SUPABASE_ANON_KEY` (instead of `SUPABASE_KEY`)
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` (instead of `CLERK_FRONTEND_API`)

### Optional Variables

These are optional and only needed if you're behind a proxy:

- `HTTP_PROXY` - HTTP proxy URL
- `HTTPS_PROXY` - HTTPS proxy URL
- `ALL_PROXY` - All traffic proxy URL

## How to Get Your Keys

### Apify API Token
1. Sign up at https://apify.com
2. Go to Settings → Integrations
3. Copy your API token

### Supabase Credentials
1. Sign up at https://supabase.com
2. Create a new project
3. Go to Settings → API
4. Copy:
   - Project URL → `SUPABASE_URL`
   - anon/public key → `SUPABASE_KEY`

### Clerk Credentials
1. Sign up at https://clerk.com
2. Create a new application
3. Go to API Keys
4. Copy:
   - Secret Key → `CLERK_SECRET_KEY`
   - Publishable Key → `CLERK_FRONTEND_API`

## Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use different keys** for development and production
3. **Rotate keys regularly** for security
4. **Use environment variables** in deployment platforms (Render, Heroku, etc.)
5. **Restrict API key permissions** when possible

## Testing Your Configuration

After setting up your environment variables, test them:

```python
import os
from dotenv import load_dotenv

load_dotenv()

print("APIFY_API_TOKEN:", "✓" if os.getenv("APIFY_API_TOKEN") else "✗")
print("SUPABASE_URL:", "✓" if os.getenv("SUPABASE_URL") else "✗")
print("SUPABASE_KEY:", "✓" if os.getenv("SUPABASE_KEY") else "✗")
print("CLERK_SECRET_KEY:", "✓" if os.getenv("CLERK_SECRET_KEY") else "✗")
print("CLERK_FRONTEND_API:", "✓" if os.getenv("CLERK_FRONTEND_API") else "✗")
```

All should show ✓ if configured correctly.

