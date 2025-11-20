-- Indexes for runs table
CREATE INDEX IF NOT EXISTS idx_runs_location_date ON runs(location, updated_date);
CREATE INDEX IF NOT EXISTS idx_runs_name ON runs(run_name);
CREATE INDEX IF NOT EXISTS idx_runs_difficulty ON runs(run_difficulty);
CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(run_status);
CREATE INDEX IF NOT EXISTS idx_runs_run_id_date ON runs(run_id, updated_date);

-- Indexes for lifts table
CREATE INDEX IF NOT EXISTS idx_lifts_location_date ON lifts(location, updated_date);
CREATE INDEX IF NOT EXISTS idx_lifts_name ON lifts(lift_name);
CREATE INDEX IF NOT EXISTS idx_lifts_status ON lifts(lift_status);
CREATE INDEX IF NOT EXISTS idx_lifts_lift_id_date ON lifts(lift_id, updated_date);

