-- Indexes for runs table
CREATE INDEX IF NOT EXISTS idx_runs_location_date ON SKI_DATA.runs(location, updated_date);
CREATE INDEX IF NOT EXISTS idx_runs_name ON SKI_DATA.runs(run_name);
CREATE INDEX IF NOT EXISTS idx_runs_difficulty ON SKI_DATA.runs(run_difficulty);
CREATE INDEX IF NOT EXISTS idx_runs_status ON SKI_DATA.runs(run_status);
CREATE INDEX IF NOT EXISTS idx_runs_run_id_date ON SKI_DATA.runs(run_id, updated_date);

-- Indexes for lifts table
CREATE INDEX IF NOT EXISTS idx_lifts_location_date ON SKI_DATA.lifts(location, updated_date);
CREATE INDEX IF NOT EXISTS idx_lifts_name ON SKI_DATA.lifts(lift_name);
CREATE INDEX IF NOT EXISTS idx_lifts_status ON SKI_DATA.lifts(lift_status);
CREATE INDEX IF NOT EXISTS idx_lifts_lift_id_date ON SKI_DATA.lifts(lift_id, updated_date);

