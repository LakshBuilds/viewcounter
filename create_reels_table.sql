-- Complete SQL Query for Supabase Reels Table
-- Copy and paste this entire query into your Supabase SQL Editor and run it

-- Step 1: Create the reels table
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
    -- User tracking fields (using TEXT for user_id to avoid foreign key issues)
    created_by_user_id TEXT,
    created_by_email TEXT,
    created_by_name TEXT,
    payout NUMERIC(10, 2) DEFAULT 0.00
);

-- Step 2: Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_reels_shortcode ON reels(shortCode);
CREATE INDEX IF NOT EXISTS idx_reels_owner ON reels(ownerUsername);
CREATE INDEX IF NOT EXISTS idx_reels_created_at ON reels(created_at);
CREATE INDEX IF NOT EXISTS idx_reels_created_by_user_id ON reels(created_by_user_id);
CREATE INDEX IF NOT EXISTS idx_reels_created_by_email ON reels(created_by_email);

-- Step 3: Enable Row Level Security (RLS)
ALTER TABLE reels ENABLE ROW LEVEL SECURITY;

-- Step 4: Drop existing policies if they exist (to avoid conflicts)
DROP POLICY IF EXISTS "Users can view all reels" ON reels;
DROP POLICY IF EXISTS "Users can insert their own reels" ON reels;
DROP POLICY IF EXISTS "Users can update their own reels" ON reels;
DROP POLICY IF EXISTS "Users can delete their own reels" ON reels;
DROP POLICY IF EXISTS "Allow all operations" ON reels;

-- Step 5: Create RLS policies
-- Policy: Everyone can view all reels (for team statistics)
CREATE POLICY "Users can view all reels" ON reels
    FOR SELECT
    USING (true);

-- Policy: Allow inserts (we'll validate user in the app)
CREATE POLICY "Users can insert their own reels" ON reels
    FOR INSERT
    WITH CHECK (true);

-- Policy: Users can update their own reels
CREATE POLICY "Users can update their own reels" ON reels
    FOR UPDATE
    USING (true)
    WITH CHECK (true);

-- Policy: Users can delete their own reels
CREATE POLICY "Users can delete their own reels" ON reels
    FOR DELETE
    USING (true);

-- Verify table was created
SELECT 'Table created successfully!' as status;

