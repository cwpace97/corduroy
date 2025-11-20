CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    run_id TEXT GENERATED ALWAYS AS (lower(hex(quote(location || run_name)))) STORED,
    location TEXT NOT NULL,
    location_id TEXT GENERATED ALWAYS AS (lower(hex(quote(location)))) STORED,
    run_name TEXT NOT NULL,
    run_difficulty TEXT,
    run_status TEXT NOT NULL,
    updated_date TEXT NOT NULL,
    run_area TEXT,
    run_groomed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);