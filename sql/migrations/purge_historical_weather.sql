-- Migration: Purge historical weather data for fresh start
-- Run this before deploying the new Open-Meteo historical weather lambda
-- This clears old SNOTEL observations and prepares for new data structure

-- Create the new historical_weather table if it doesn't exist
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

-- Purge all existing SNOTEL observations (fresh start)
-- This removes old hourly data that was fetched every 3 hours
-- TRUNCATE TABLE WEATHER_DATA.snotel_observations;

-- Purge any existing historical_weather data (fresh start)
TRUNCATE TABLE WEATHER_DATA.historical_weather;

-- Verify tables are empty
-- SELECT 'snotel_observations' as table_name, COUNT(*) as row_count FROM WEATHER_DATA.snotel_observations
-- UNION ALL
SELECT 'historical_weather' as table_name, COUNT(*) as row_count FROM WEATHER_DATA.historical_weather;

-- Add snowfall_total_in column to track daily snowfall if not exists
-- This is computed from Open-Meteo hourly data
-- Note: This is handled in the resolver, not stored in DB

COMMENT ON TABLE WEATHER_DATA.historical_weather IS 'Hourly temperature and precipitation data from Open-Meteo API for resort locations';
COMMENT ON COLUMN WEATHER_DATA.historical_weather.temperature_f IS 'Hourly temperature in Fahrenheit from Open-Meteo';
COMMENT ON COLUMN WEATHER_DATA.historical_weather.precipitation_in IS 'Hourly precipitation in inches from Open-Meteo';
COMMENT ON COLUMN WEATHER_DATA.historical_weather.snowfall_in IS 'Hourly snowfall in inches from Open-Meteo';

