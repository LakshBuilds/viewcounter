-- Add payout column to reels table
-- Run this SQL in your Supabase SQL Editor

-- Check if column exists, if not add it
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'reels' 
        AND column_name = 'payout'
    ) THEN
        ALTER TABLE reels ADD COLUMN payout NUMERIC(10, 2) DEFAULT 0.00;
    ELSE
        -- If column exists but is wrong type, alter it
        ALTER TABLE reels ALTER COLUMN payout TYPE NUMERIC(10, 2);
        ALTER TABLE reels ALTER COLUMN payout SET DEFAULT 0.00;
    END IF;
END $$;

-- Update any existing NULL values to 0.00
UPDATE reels SET payout = 0.00 WHERE payout IS NULL;

-- Verify the column was added/updated
SELECT column_name, data_type, numeric_precision, numeric_scale 
FROM information_schema.columns 
WHERE table_name = 'reels' 
AND column_name = 'payout';

