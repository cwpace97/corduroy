-- Table for weather forecasts from multiple sources
CREATE TABLE IF NOT EXISTS WEATHER_DATA.weather_forecasts (
    id SERIAL PRIMARY KEY,
    resort_name VARCHAR(100) NOT NULL,
    source VARCHAR(255) NOT NULL,  -- 'NWS' or 'OPEN_METEO'
    forecast_time TIMESTAMP NOT NULL,  -- When the forecast was generated/fetched
    valid_time TIMESTAMP NOT NULL,  -- When this forecast is valid for
    
    -- Temperature (Fahrenheit)
    temp_high_f DECIMAL(5, 1),
    temp_low_f DECIMAL(5, 1),
    
    -- Precipitation
    snow_amount_in DECIMAL(6, 2),  -- Expected snowfall in inches
    precip_amount_in DECIMAL(6, 2),  -- Total precipitation (rain + snow)
    precip_prob_pct INTEGER,  -- Probability of precipitation (0-100)
    
    -- Wind
    wind_speed_mph DECIMAL(5, 1),
    wind_direction_deg INTEGER,  -- Wind direction in degrees (0-360)
    wind_gust_mph DECIMAL(5, 1),
    
    -- Conditions
    conditions_text VARCHAR(255),  -- e.g., "Snow", "Partly Cloudy", "Clear"
    icon_code VARCHAR(255),  -- Icon identifier from API (can be full URLs)
    
    -- Additional metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure we don't duplicate forecasts for same resort/source/valid_time
    UNIQUE(resort_name, source, valid_time)
);

