CREATE TABLE IF NOT EXISTS SKI_DATA.runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id TEXT GENERATED ALWAYS AS (md5(location || run_name)) STORED,
    location TEXT NOT NULL,
    location_id TEXT GENERATED ALWAYS AS (md5(location)) STORED,
    run_name TEXT NOT NULL,
    run_difficulty TEXT,
    run_status TEXT NOT NULL,
    updated_date TEXT NOT NULL,
    run_area TEXT,
    run_groomed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);