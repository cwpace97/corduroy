-- View: Daily weather data from historical observations
-- Now uses daily records directly (observation_hour = 0)

CREATE OR REPLACE VIEW WEATHER_DATA.historical_weather_daily AS
SELECT 
    resort_name,
    observation_date,
    temp_min_f,
    temperature_f AS temp_max_f,
    (COALESCE(temperature_f, 0) + COALESCE(temp_min_f, 0)) / 2.0 AS temp_avg_f,
    precipitation_in AS precip_total_in,
    snowfall_in AS snowfall_total_in
FROM WEATHER_DATA.historical_weather
WHERE observation_hour = 0
ORDER BY resort_name, observation_date;

COMMENT ON VIEW WEATHER_DATA.historical_weather_daily IS 'Daily weather summaries from Open-Meteo daily data.';

