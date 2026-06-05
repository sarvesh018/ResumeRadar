-- Run this if you already have the database set up
-- (If starting fresh, re-run init-schemas.sql instead after updating it)

ALTER TABLE profile_db.profiles
ADD COLUMN IF NOT EXISTS technical_skills JSONB DEFAULT '[]'::jsonb;

-- Verify
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'profile_db'
AND table_name = 'profiles'
AND column_name = 'technical_skills';