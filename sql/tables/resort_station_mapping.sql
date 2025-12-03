-- Table for resort-station mapping
CREATE TABLE IF NOT EXISTS WEATHER_DATA.resort_station_mapping (
    id SERIAL PRIMARY KEY,
    resort_name VARCHAR(100) NOT NULL,
    station_triplet VARCHAR(50) NOT NULL REFERENCES WEATHER_DATA.snotel_stations(station_triplet),
    distance_miles DECIMAL(6, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(resort_name, station_triplet)
);

