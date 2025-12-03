-- Table for SNOTEL weather observations
CREATE TABLE IF NOT EXISTS WEATHER_DATA.snotel_observations (
    id SERIAL PRIMARY KEY,
    station_triplet VARCHAR(50) NOT NULL REFERENCES WEATHER_DATA.snotel_stations(station_triplet),
    observation_date DATE NOT NULL,
    observation_hour INTEGER,  -- NULL for daily data, 0-23 for hourly
    duration VARCHAR(10) NOT NULL,  -- 'DAILY' or 'HOURLY'
    
    -- Snow measurements
    snow_water_equivalent_in DECIMAL(6, 1),  -- WTEQ
    snow_depth_in DECIMAL(6, 1),              -- SNWD
    snow_density_pct DECIMAL(5, 1),           -- SNDN
    snow_rain_ratio DECIMAL(6, 2),            -- SNRR
    
    -- Temperature measurements (Fahrenheit)
    temp_min_f DECIMAL(5, 1),                 -- TMIN
    temp_max_f DECIMAL(5, 1),                 -- TMAX
    temp_avg_f DECIMAL(5, 1),                 -- TAVG
    temp_observed_f DECIMAL(5, 1),            -- TOBS
    
    -- Precipitation
    precip_accum_in DECIMAL(6, 2),            -- PREC
    precip_increment_in DECIMAL(6, 2),        -- PRCP
    
    -- Wind
    wind_speed_avg_mph DECIMAL(5, 1),         -- WSPDV
    wind_speed_max_mph DECIMAL(5, 1),         -- WSPDX
    wind_direction_avg_deg INTEGER,           -- WDIRV
    
    -- Humidity
    relative_humidity_avg_pct DECIMAL(5, 1),  -- RHUMV
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(station_triplet, observation_date, observation_hour, duration)
);

