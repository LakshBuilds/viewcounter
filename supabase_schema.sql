-- Create reels table in Supabase
-- Run this SQL in your Supabase SQL Editor

-- Drop table if exists (for fresh start - comment out if you have existing data)
-- DROP TABLE IF EXISTS reels CASCADE;

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
    -- User tracking fields
    created_by_user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_by_email TEXT,
    created_by_name TEXT
);

-- Create index on shortCode for faster lookups
CREATE INDEX IF NOT EXISTS idx_reels_shortcode ON reels(shortCode);

-- Create index on ownerUsername for filtering
CREATE INDEX IF NOT EXISTS idx_reels_owner ON reels(ownerUsername);

-- Create index on created_at for sorting
CREATE INDEX IF NOT EXISTS idx_reels_created_at ON reels(created_at);

-- Create index on user_id for user-specific queries
CREATE INDEX IF NOT EXISTS idx_reels_created_by_user_id ON reels(created_by_user_id);
CREATE INDEX IF NOT EXISTS idx_reels_created_by_email ON reels(created_by_email);

-- Enable Row Level Security
ALTER TABLE reels ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view all reels" ON reels;
DROP POLICY IF EXISTS "Users can insert their own reels" ON reels;
DROP POLICY IF EXISTS "Users can update their own reels" ON reels;
DROP POLICY IF EXISTS "Users can delete their own reels" ON reels;

-- Create policy: Users can view all reels (for overall statistics and team view)
CREATE POLICY "Users can view all reels" ON reels
    FOR SELECT
    USING (true);

-- Create policy: Users can insert their own reels
CREATE POLICY "Users can insert their own reels" ON reels
    FOR INSERT
    WITH CHECK (auth.uid() = created_by_user_id OR created_by_user_id IS NULL);

-- Create policy: Users can update their own reels
CREATE POLICY "Users can update their own reels" ON reels
    FOR UPDATE
    USING (auth.uid() = created_by_user_id)
    WITH CHECK (auth.uid() = created_by_user_id);

-- Create policy: Users can delete their own reels
CREATE POLICY "Users can delete their own reels" ON reels
    FOR DELETE
    USING (auth.uid() = created_by_user_id);
