-- View to easily query weather data by resort
CREATE OR REPLACE VIEW WEATHER_DATA.v_resort_weather AS
SELECT 
    rsm.resort_name,
    rsm.distance_miles,
    ss.station_name,
    ss.station_triplet,
    ss.elevation_ft,
    so.observation_date,
    so.observation_hour,
    so.duration,
    so.snow_water_equivalent_in,
    so.snow_depth_in,
    so.snow_density_pct,
    so.snow_rain_ratio,
    so.temp_min_f,
    so.temp_max_f,
    so.temp_avg_f,
    so.temp_observed_f,
    so.precip_accum_in,
    so.precip_increment_in,
    so.wind_speed_avg_mph,
    so.wind_speed_max_mph,
    so.wind_direction_avg_deg,
    so.relative_humidity_avg_pct
FROM WEATHER_DATA.resort_station_mapping rsm
JOIN WEATHER_DATA.snotel_stations ss ON rsm.station_triplet = ss.station_triplet
JOIN WEATHER_DATA.snotel_observations so ON ss.station_triplet = so.station_triplet;

