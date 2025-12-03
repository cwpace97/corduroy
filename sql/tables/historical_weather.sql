-- Table for historical weather observations from Open-Meteo API
-- Stores hourly temperature and precipitation data for resorts
CREATE TABLE IF NOT EXISTS WEATHER_DATA.historical_weather (
    id SERIAL PRIMARY KEY,
    resort_name VARCHAR(100) NOT NULL,
    observation_date DATE NOT NULL,
    observation_hour INTEGER NOT NULL,  -- 0-23
    
    -- Temperature (Fahrenheit)
    temperature_f DECIMAL(5, 1),
    
    -- Precipitation
    precipitation_in DECIMAL(6, 3),  -- Hourly precipitation in inches
    snowfall_in DECIMAL(6, 2),       -- Hourly snowfall in inches
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure we don't duplicate observations for same resort/date/hour
    UNIQUE(resort_name, observation_date, observation_hour)
);

-- Index for efficient querying by resort and date range
CREATE INDEX IF NOT EXISTS idx_historical_weather_resort_date 
ON WEATHER_DATA.historical_weather(resort_name, observation_date);

