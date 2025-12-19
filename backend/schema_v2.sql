-- Add new columns for RSS maintenance
ALTER TABLE feeds ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE feeds ADD COLUMN IF NOT EXISTS last_fetch_status TEXT;
ALTER TABLE feeds ADD COLUMN IF NOT EXISTS last_fetch_time TIMESTAMP;
ALTER TABLE feeds ADD COLUMN IF NOT EXISTS failure_count INTEGER DEFAULT 0;

-- Optional: Create index for faster active feed lookup
CREATE INDEX IF NOT EXISTS idx_feeds_active ON feeds(is_active);
