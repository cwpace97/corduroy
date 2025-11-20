CREATE TABLE IF NOT EXISTS lifts (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    lift_id TEXT GENERATED ALWAYS AS (lower(hex(quote(location || lift_name)))) STORED,
    location TEXT NOT NULL,
    location_id TEXT GENERATED ALWAYS AS (lower(hex(quote(location)))) STORED,
    lift_name TEXT NOT NULL,
    lift_status TEXT NOT NULL,
    lift_type TEXT,
    updated_date TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);;