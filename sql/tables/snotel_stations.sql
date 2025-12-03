-- Table for SNOTEL stations
CREATE TABLE IF NOT EXISTS WEATHER_DATA.snotel_stations (
    station_triplet VARCHAR(50) PRIMARY KEY,
    station_name VARCHAR(255),
    latitude DECIMAL(10, 6),
    longitude DECIMAL(10, 6),
    elevation_ft INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

