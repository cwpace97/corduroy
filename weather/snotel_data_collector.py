#!/usr/bin/env python3
"""
SNOTEL Data Collector

Queries USDA AWDB REST API for SNOTEL weather station data and generates
SQL INSERT statements for the WEATHER_DATA schema in PostgreSQL.
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Optional
import os


# SNOTEL elements relevant for ski resort weather/snow data
SNOW_WEATHER_ELEMENTS = [
    "WTEQ",    # Snow Water Equivalent
    "SNWD",    # Snow Depth
    "SNDN",    # Snow Density
    "SNRR",    # Snow Rain Ratio
    "TMIN",    # Temperature Minimum
    "TMAX",    # Temperature Maximum
    "TAVG",    # Temperature Average
    "TOBS",    # Temperature Observed
    "PREC",    # Precipitation Accumulation
    "PRCP",    # Precipitation Increment
    "WSPDV",   # Wind Speed Average
    "WSPDX",   # Wind Speed Maximum
    "WDIRV",   # Wind Direction Average
    "RHUMV",   # Relative Humidity Average
]


class SNOTELDataCollector:
    """Collects SNOTEL data for ski resorts and generates SQL statements."""
    
    BASE_URL = "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1"
    
    def __init__(self, mapping_file: str = "resort_snotel_mapping.json", resort_filter: Optional[str] = None):
        """
        Initialize the collector with resort-SNOTEL mapping.
        
        Args:
            mapping_file: Path to the JSON file containing resort-SNOTEL mappings
            resort_filter: Optional resort name to filter data for (case-insensitive)
        """
        self.mapping_file = mapping_file
        self.resort_filter = resort_filter
        self.resort_mapping = self._load_mapping()
        self.unique_stations = self._extract_unique_stations()
        self.resort_station_lookup = self._build_resort_station_lookup()
    
    def _load_mapping(self) -> dict:
        """Load the resort-SNOTEL mapping from JSON file."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        mapping_path = os.path.join(script_dir, self.mapping_file)
        
        with open(mapping_path, "r") as f:
            return json.load(f)
    
    def _extract_unique_stations(self) -> list[str]:
        """Extract unique SNOTEL station triplets from the mapping."""
        stations = set()
        
        for resort_name, resort_data in self.resort_mapping.items():
            # If resort filter is set, only include stations for matching resort
            if self.resort_filter:
                if resort_name.lower() != self.resort_filter.lower():
                    continue
            
            for key in resort_data.keys():
                # SNOTEL triplets contain ":" (e.g., "415:CO:SNTL")
                # Resort names don't have colons
                if ":" in key:
                    stations.add(key)
        
        return sorted(list(stations))
    
    def _build_resort_station_lookup(self) -> dict:
        """Build a lookup from station triplet to list of resorts it serves."""
        lookup = {}
        
        for resort_name, resort_data in self.resort_mapping.items():
            # If resort filter is set, only include mappings for matching resort
            if self.resort_filter:
                if resort_name.lower() != self.resort_filter.lower():
                    continue
            
            for key, station_info in resort_data.items():
                if ":" in key:  # It's a SNOTEL station
                    if key not in lookup:
                        lookup[key] = []
                    lookup[key].append({
                        "resort": resort_name,
                        "station_name": station_info.get("name", ""),
                        "distance_miles": station_info.get("distance_miles", 0)
                    })
        
        return lookup
    
    def fetch_snotel_data(
        self,
        begin_date: str,
        end_date: str,
        duration: str = "DAILY",
        elements: Optional[list[str]] = None
    ) -> list[dict]:
        """
        Fetch SNOTEL data from the USDA AWDB REST API.
        
        Args:
            begin_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            duration: Data duration - "HOURLY" or "DAILY"
            elements: List of element codes to fetch (defaults to SNOW_WEATHER_ELEMENTS)
        
        Returns:
            List of station data dictionaries from the API
        """
        if elements is None:
            elements = SNOW_WEATHER_ELEMENTS
        
        # Join station triplets with comma
        station_triplets = ",".join(self.unique_stations)
        
        # Join elements with comma
        elements_str = ",".join(elements)
        
        params = {
            "stationTriplets": station_triplets,
            "elements": elements_str,
            "duration": duration,
            "beginDate": begin_date,
            "endDate": end_date,
            "periodRef": "END",
            "centralTendencyType": "NONE",
            "returnFlags": "false",
            "returnOriginalValues": "false",
            "returnSuspectData": "false"
        }
        
        url = f"{self.BASE_URL}/data"
        
        print(f"Fetching SNOTEL data from {begin_date} to {end_date}...")
        print(f"Stations: {len(self.unique_stations)}")
        print(f"Elements: {elements_str}")
        print(f"Duration: {duration}")
        
        response = requests.get(url, params=params, headers={"accept": "application/json"})
        response.raise_for_status()
        
        data = response.json()
        print(f"Received data for {len(data)} stations")
        
        return data
    
    def generate_station_inserts(self) -> str:
        """Generate SQL INSERT statements for SNOTEL stations."""
        inserts = []
        
        for station_triplet in self.unique_stations:
            # Find station info from mapping
            station_name = ""
            latitude = None
            longitude = None
            
            for resort_data in self.resort_mapping.values():
                if station_triplet in resort_data:
                    station_info = resort_data[station_triplet]
                    station_name = station_info.get("name", "")
                    latitude = station_info.get("latitude")
                    longitude = station_info.get("longitude")
                    break
            
            if latitude and longitude:
                insert = f"""INSERT INTO WEATHER_DATA.snotel_stations (station_triplet, station_name, latitude, longitude)
VALUES ('{station_triplet}', '{station_name}', {latitude}, {longitude})
ON CONFLICT (station_triplet) DO UPDATE SET
    station_name = EXCLUDED.station_name,
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude;"""
                inserts.append(insert)
        
        return "\n\n".join(inserts)
    
    def generate_resort_mapping_inserts(self) -> str:
        """Generate SQL INSERT statements for resort-station mappings."""
        inserts = []
        
        for station_triplet, resorts in self.resort_station_lookup.items():
            for resort_info in resorts:
                resort_name = resort_info["resort"]
                distance = resort_info["distance_miles"]
                
                insert = f"""INSERT INTO WEATHER_DATA.resort_station_mapping (resort_name, station_triplet, distance_miles)
VALUES ('{resort_name}', '{station_triplet}', {distance})
ON CONFLICT (resort_name, station_triplet) DO UPDATE SET
    distance_miles = EXCLUDED.distance_miles;"""
                inserts.append(insert)
        
        return "\n\n".join(inserts)
    
    def generate_observation_inserts(self, api_data: list[dict], duration: str = "DAILY") -> str:
        """
        Generate SQL INSERT statements for SNOTEL observations.
        
        Args:
            api_data: Response data from the USDA AWDB API
            duration: "DAILY" or "HOURLY"
        
        Returns:
            SQL INSERT statements as a string
        """
        inserts = []
        
        # Element code to column name mapping
        element_mapping = {
            "WTEQ": "snow_water_equivalent_in",
            "SNWD": "snow_depth_in",
            "SNDN": "snow_density_pct",
            "SNRR": "snow_rain_ratio",
            "TMIN": "temp_min_f",
            "TMAX": "temp_max_f",
            "TAVG": "temp_avg_f",
            "TOBS": "temp_observed_f",
            "PREC": "precip_accum_in",
            "PRCP": "precip_increment_in",
            "WSPDV": "wind_speed_avg_mph",
            "WSPDX": "wind_speed_max_mph",
            "WDIRV": "wind_direction_avg_deg",
            "RHUMV": "relative_humidity_avg_pct",
        }
        
        for station_data in api_data:
            station_triplet = station_data.get("stationTriplet", "")
            
            if not station_triplet:
                continue
            
            # Collect all data points by date/time
            observations = {}  # key: (date, hour) -> dict of values
            
            for data_item in station_data.get("data", []):
                element_code = data_item.get("stationElement", {}).get("elementCode", "")
                
                if element_code not in element_mapping:
                    continue
                
                column_name = element_mapping[element_code]
                
                for value_entry in data_item.get("values", []):
                    date_str = value_entry.get("date", "")
                    value = value_entry.get("value")
                    
                    if not date_str or value is None:
                        continue
                    
                    # Parse date - format can be "YYYY-MM-DD" or "YYYY-MM-DD HH:MM"
                    if " " in date_str:
                        date_part = date_str.split(" ")[0]
                        time_part = date_str.split(" ")[1]
                        hour = int(time_part.split(":")[0])
                    else:
                        date_part = date_str
                        hour = None
                    
                    key = (date_part, hour)
                    
                    if key not in observations:
                        observations[key] = {}
                    
                    observations[key][column_name] = value
            
            # Generate INSERT for each observation
            for (date_part, hour), values in observations.items():
                columns = ["station_triplet", "observation_date", "observation_hour", "duration"]
                hour_value = "NULL" if hour is None else str(hour)
                sql_values = [f"'{station_triplet}'", f"'{date_part}'", hour_value, f"'{duration}'"]
                
                for col_name, val in values.items():
                    columns.append(col_name)
                    sql_values.append(str(val) if val is not None else "NULL")
                
                columns_str = ", ".join(columns)
                values_str = ", ".join(sql_values)
                
                # Build update clause for upsert
                update_cols = [col for col in columns if col not in 
                              ["station_triplet", "observation_date", "observation_hour", "duration"]]
                update_clause = ", ".join([f"{col} = EXCLUDED.{col}" for col in update_cols])
                
                if update_clause:
                    insert = f"""INSERT INTO WEATHER_DATA.snotel_observations ({columns_str})
VALUES ({values_str})
ON CONFLICT (station_triplet, observation_date, observation_hour, duration) DO UPDATE SET
    {update_clause};"""
                else:
                    insert = f"""INSERT INTO WEATHER_DATA.snotel_observations ({columns_str})
VALUES ({values_str})
ON CONFLICT (station_triplet, observation_date, observation_hour, duration) DO NOTHING;"""
                
                inserts.append(insert)
        
        return "\n\n".join(inserts)
    
    def collect_and_generate_sql(
        self,
        begin_date: str,
        end_date: str,
        duration: str = "DAILY",
        output_file: Optional[str] = None
    ) -> str:
        """
        Main method to collect SNOTEL data and generate complete SQL.
        
        Args:
            begin_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            duration: "DAILY" or "HOURLY"
            output_file: Optional path to write SQL output
        
        Returns:
            Complete SQL statements as a string
        """
        # Fetch data from API
        api_data = self.fetch_snotel_data(begin_date, end_date, duration)
        
        # Generate all SQL components (INSERT statements only - schema is handled by init_db.py)
        sql_parts = [
            "-- SNOTEL Data Import Script",
            f"-- Generated: {datetime.now().isoformat()}",
            f"-- Date Range: {begin_date} to {end_date}",
            f"-- Duration: {duration}",
            f"-- Stations: {len(self.unique_stations)}",
            "",
            "-- ============================================",
            "-- SNOTEL STATION DATA",
            "-- ============================================",
            self.generate_station_inserts(),
            "",
            "-- ============================================",
            "-- RESORT-STATION MAPPINGS",
            "-- ============================================",
            self.generate_resort_mapping_inserts(),
            "",
            "-- ============================================",
            "-- WEATHER OBSERVATIONS",
            "-- ============================================",
            self.generate_observation_inserts(api_data, duration),
        ]
        
        complete_sql = "\n".join(sql_parts)
        
        if output_file:
            with open(output_file, "w") as f:
                f.write(complete_sql)
            print(f"SQL written to: {output_file}")
        
        return complete_sql


def main():
    """Main entry point for the SNOTEL data collector."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Collect SNOTEL data and generate SQL INSERT statements"
    )
    parser.add_argument(
        "--begin-date",
        type=str,
        default=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
        help="Start date (YYYY-MM-DD). Default: 7 days ago"
    )
    parser.add_argument(
        "--end-date",
        type=str,
        default=datetime.now().strftime("%Y-%m-%d"),
        help="End date (YYYY-MM-DD). Default: today"
    )
    parser.add_argument(
        "--duration",
        type=str,
        choices=["DAILY", "HOURLY"],
        default="DAILY",
        help="Data duration. Default: DAILY"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output SQL file path. If not specified, prints to stdout"
    )
    parser.add_argument(
        "--mapping-file",
        type=str,
        default="resort_snotel_mapping.json",
        help="Path to resort-SNOTEL mapping JSON file"
    )
    parser.add_argument(
        "--resort",
        type=str,
        default=None,
        help="Filter to a specific resort (case-insensitive). E.g., --resort Steamboat"
    )
    
    args = parser.parse_args()
    
    collector = SNOTELDataCollector(mapping_file=args.mapping_file, resort_filter=args.resort)
    
    if args.resort:
        print(f"Filtering for resort: {args.resort}")
    
    print(f"Unique SNOTEL stations: {collector.unique_stations}")
    print(f"Total stations: {len(collector.unique_stations)}")
    print()
    
    sql = collector.collect_and_generate_sql(
        begin_date=args.begin_date,
        end_date=args.end_date,
        duration=args.duration,
        output_file=args.output
    )
    
    if not args.output:
        print("\n" + "=" * 60)
        print("GENERATED SQL:")
        print("=" * 60)
        print(sql)


if __name__ == "__main__":
    main()

