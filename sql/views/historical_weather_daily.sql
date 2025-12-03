-- View: Pre-aggregated daily weather data from hourly observations
-- This reduces the response size by aggregating hourly data into daily summaries

CREATE OR REPLACE VIEW WEATHER_DATA.historical_weather_daily AS
SELECT 
    resort_name,
    observation_date,
    MIN(temperature_f) AS temp_min_f,
    MAX(temperature_f) AS temp_max_f,
    AVG(temperature_f) AS temp_avg_f,
    SUM(precipitation_in) AS precip_total_in,
    SUM(snowfall_in) AS snowfall_total_in,
    COUNT(*) AS hour_count
FROM WEATHER_DATA.historical_weather
GROUP BY resort_name, observation_date
ORDER BY resort_name, observation_date;

COMMENT ON VIEW WEATHER_DATA.historical_weather_daily IS 'Pre-aggregated daily weather summaries from hourly Open-Meteo data.';

