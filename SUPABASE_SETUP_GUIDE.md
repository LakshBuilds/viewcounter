# Supabase Setup Guide - Step by Step

## Step 1: Create the Table in Supabase

1. Go to your Supabase project: https://supabase.com/dashboard
2. Click on **SQL Editor** in the left sidebar
3. Click **New Query**
4. Copy the entire contents of `create_reels_table.sql` file
5. Paste it into the SQL Editor
6. Click **Run** (or press Ctrl+Enter)
7. You should see "Table created successfully!" message

## Step 2: Verify Table Creation

1. Go to **Table Editor** in the left sidebar
2. You should see a table named `reels`
3. Click on it to see all the columns

## Step 3: Check Your Supabase Credentials

Your credentials should be:
- **URL**: `https://hdvwwhsiqbtrttzvzyrj.supabase.co`
- **Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imhkdnd3aHNpcWJ0cnR0enZ6eXJqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM0OTU5MDcsImV4cCI6MjA3OTA3MTkwN30.1mgeIMeElVNYljvQ-YYiqLxag92px2sf_YUF3EAHhrA`

## Step 4: Test Connection in Dashboard

1. Open the dashboard at `http://localhost:8501`
2. In the "Initial Setup" section, make sure your credentials are entered
3. You should see: "✅ Supabase configured and connected!"

## Troubleshooting

### If you get "Failed to connect to Supabase":
1. **Check your project is active**: Make sure your Supabase project isn't paused
2. **Verify credentials**: Double-check the URL and Key match exactly
3. **Check API settings**: Go to Settings → API and verify the anon key
4. **Test in browser**: Try accessing `https://hdvwwhsiqbtrttzvzyrj.supabase.co` - it should show a JSON response

### If table creation fails:
1. Make sure you're using the **SQL Editor** (not Table Editor)
2. Run the query in parts if needed (create table first, then indexes, then policies)
3. Check for any error messages in the SQL Editor output

### If authentication doesn't work:
1. Go to **Authentication** → **Providers** in Supabase
2. Make sure **Email** provider is enabled
3. Check **Authentication** → **Settings** for any restrictions

## Quick SQL Query (Copy This)

```sql
CREATE TABLE IF NOT EXISTS reels (
    id TEXT PRIMARY KEY,
    shortCode TEXT,
    ownerUsername TEXT,
    ownerFullName TEXT,
    ownerId TEXT,
    caption TEXT,
    likesCount INTEGER DEFAULT 0,
    commentsCount INTEGER DEFAULT 0,
    videoViewCount INTEGER DEFAULT 0,
    videoPlayCount INTEGER DEFAULT 0,
    videoWatchCount INTEGER DEFAULT 0,
    repostCount INTEGER DEFAULT 0,
    savedCount INTEGER DEFAULT 0,
    sentCount INTEGER DEFAULT 0,
    shareCount INTEGER DEFAULT 0,
    locationName TEXT,
    timestamp TIMESTAMPTZ,
    takenAt TIMESTAMPTZ,
    lastUpdatedAt TIMESTAMPTZ,
    publishedTime TIMESTAMPTZ,
    displayUrl TEXT,
    videoUrl TEXT,
    thumbnailUrl TEXT,
    audioName TEXT,
    audioUrl TEXT,
    productType TEXT,
    url TEXT,
    permalink TEXT,
    inputUrl TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by_user_id TEXT,
    created_by_email TEXT,
    created_by_name TEXT
);

CREATE INDEX IF NOT EXISTS idx_reels_shortcode ON reels(shortCode);
CREATE INDEX IF NOT EXISTS idx_reels_owner ON reels(ownerUsername);
CREATE INDEX IF NOT EXISTS idx_reels_created_at ON reels(created_at);
CREATE INDEX IF NOT EXISTS idx_reels_created_by_user_id ON reels(created_by_user_id);
CREATE INDEX IF NOT EXISTS idx_reels_created_by_email ON reels(created_by_email);

ALTER TABLE reels ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view all reels" ON reels;
DROP POLICY IF EXISTS "Users can insert their own reels" ON reels;
DROP POLICY IF EXISTS "Users can update their own reels" ON reels;
DROP POLICY IF EXISTS "Users can delete their own reels" ON reels;

CREATE POLICY "Users can view all reels" ON reels FOR SELECT USING (true);
CREATE POLICY "Users can insert their own reels" ON reels FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can update their own reels" ON reels FOR UPDATE USING (true) WITH CHECK (true);
CREATE POLICY "Users can delete their own reels" ON reels FOR DELETE USING (true);
```

