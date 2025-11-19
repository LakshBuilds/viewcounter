# Instagram Creators Dashboard

A Streamlit dashboard for tracking Instagram reel performance with team collaboration features, built with Clerk authentication and Supabase database integration.

## Features

- 🔐 **Clerk Authentication** - Secure login/signup with @buyhatke.com email validation
- 📊 **Reel Analytics** - Track likes, comments, views, and engagement metrics
- 👥 **Team Collaboration** - View personal reels or all team reels
- 💰 **Payout Tracking** - Manually track and edit payout amounts for each reel
- 🔄 **Auto Refresh** - Refresh all reel data with one click
- 📈 **Creator Statistics** - Individual and team-wide performance metrics
- 🗑️ **Delete Functionality** - Remove reels from your personal collection

## Prerequisites

- Python 3.10+
- Apify API token
- Supabase account (for database)
- Clerk account (for authentication)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/LakshBuilds/viewcounter.git
   cd viewcounter
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # or
   source .venv/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   APIFY_API_TOKEN=your_apify_api_token_here
   SUPABASE_URL=your_supabase_url_here
   SUPABASE_KEY=your_supabase_anon_key_here
   CLERK_SECRET_KEY=your_clerk_secret_key_here
   CLERK_FRONTEND_API=your_clerk_publishable_key_here
   ```

5. **Set up Supabase database**
   
   Run the SQL script in your Supabase SQL Editor:
   - See `create_reels_table.sql` for the main table schema
   - See `add_payout_column.sql` to add the payout column (if needed)

6. **Run the application**
   ```bash
   streamlit run app.py
   ```

   The dashboard will launch on `http://localhost:8501`

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `APIFY_API_TOKEN` | Your Apify API token for fetching Instagram reel data | Yes |
| `SUPABASE_URL` | Your Supabase project URL | Yes |
| `SUPABASE_KEY` | Your Supabase anonymous/public key | Yes |
| `CLERK_SECRET_KEY` | Your Clerk secret key for authentication | Yes |
| `CLERK_FRONTEND_API` | Your Clerk publishable key | Yes |

## Database Setup

1. Go to your Supabase dashboard
2. Open the SQL Editor
3. Run the SQL from `create_reels_table.sql` to create the reels table
4. If you need the payout column, run `add_payout_column.sql`

## Using the Dashboard

1. **Sign Up/Login**: Use your @buyhatke.com email to create an account
2. **Add Reels**: 
   - Single URL: Paste one Instagram reel URL at a time
   - Bulk Import: Paste multiple URLs (one per line)
3. **View Modes**:
   - **Your Reels**: See only your added reels with edit/delete options
   - **All Team Reels**: See all team reels with aggregated statistics
4. **Edit Payout**: Click on the payout field in the sheet to edit values
5. **Refresh Data**: Click "Refresh All Reels" to update metrics from Apify
6. **Logout**: Click on your avatar to show logout option

## Project Structure

```
viewcounter/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── create_reels_table.sql      # Database schema
├── add_payout_column.sql       # Payout column migration
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Features in Detail

### Authentication
- Clerk-based authentication
- Email validation (only @buyhatke.com emails allowed)
- Session persistence across page refreshes
- Admin role support

### Data Management
- Automatic saving to Supabase
- User-specific reel tracking
- Bulk import support
- Data refresh with payout preservation

### Analytics
- Total likes, comments, views across all reels
- Individual creator statistics
- Team-wide aggregated metrics
- Creator leaderboard

## Development

The app uses:
- **Streamlit** for the web interface
- **Apify Client** for Instagram data scraping
- **Supabase** for data persistence
- **Clerk** for authentication
- **Pandas** for data manipulation

## License

This project is private and proprietary to buyhatke.
