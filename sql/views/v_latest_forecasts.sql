-- View to get latest forecasts for each resort/source combination
CREATE OR REPLACE VIEW WEATHER_DATA.v_latest_forecasts AS
SELECT DISTINCT ON (resort_name, source)
    id,
    resort_name,
    source,
    forecast_time,
    valid_time,
    temp_high_f,
    temp_low_f,
    snow_amount_in,
    precip_amount_in,
    precip_prob_pct,
    wind_speed_mph,
    wind_direction_deg,
    wind_gust_mph,
    conditions_text,
    icon_code,
    created_at
FROM WEATHER_DATA.weather_forecasts
WHERE valid_time >= CURRENT_TIMESTAMP
ORDER BY resort_name, source, forecast_time DESC;

