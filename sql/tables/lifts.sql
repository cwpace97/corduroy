CREATE TABLE IF NOT EXISTS SKI_DATA.lifts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lift_id TEXT GENERATED ALWAYS AS (md5(location || lift_name)) STORED,
    location TEXT NOT NULL,
    location_id TEXT GENERATED ALWAYS AS (md5(location)) STORED,
    lift_name TEXT NOT NULL,
    lift_status TEXT NOT NULL,
    lift_type TEXT,
    updated_date TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);