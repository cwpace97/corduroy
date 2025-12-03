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

-- Indexes for SNOTEL observations table
CREATE INDEX IF NOT EXISTS idx_snotel_obs_date 
    ON WEATHER_DATA.snotel_observations(observation_date);
CREATE INDEX IF NOT EXISTS idx_snotel_obs_station_date 
    ON WEATHER_DATA.snotel_observations(station_triplet, observation_date);

-- Indexes for weather forecasts table
CREATE INDEX IF NOT EXISTS idx_forecasts_resort_valid_time 
    ON WEATHER_DATA.weather_forecasts(resort_name, valid_time);
CREATE INDEX IF NOT EXISTS idx_forecasts_forecast_time 
    ON WEATHER_DATA.weather_forecasts(forecast_time);
CREATE INDEX IF NOT EXISTS idx_forecasts_source 
    ON WEATHER_DATA.weather_forecasts(source);

