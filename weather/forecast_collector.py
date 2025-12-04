#!/usr/bin/env python3
"""
Weather Forecast Collector

Fetches weather forecasts from Open-Meteo API for Colorado ski resorts.
Normalizes the data into a common schema and generates SQL INSERT statements.
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import os
import time


class ForecastCollector:
    """Collects weather forecasts from Open-Meteo for ski resorts."""
    
    OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"
    
    def __init__(self, mapping_file: str = "resort_snotel_mapping.json"):
        """
        Initialize the collector with resort coordinates.
        
        Args:
            mapping_file: Path to the JSON file containing resort coordinates
        """
        self.mapping_file = mapping_file
        self.resort_coordinates = self._load_resort_coordinates()
    
    def _load_resort_coordinates(self) -> Dict[str, Dict[str, float]]:
        """Load resort coordinates from mapping file."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        mapping_path = os.path.join(script_dir, self.mapping_file)
        
        with open(mapping_path, "r") as f:
            mapping = json.load(f)
        
        # Extract resort coordinates (the entry without ":" in key)
        coordinates = {}
        for resort_name, resort_data in mapping.items():
            for key, value in resort_data.items():
                if ":" not in key:  # This is the resort itself, not a SNOTEL station
                    coordinates[resort_name] = {
                        "latitude": value.get("latitude"),
                        "longitude": value.get("longitude")
                    }
                    break
        
        return coordinates
    
    def _fetch_open_meteo_forecast(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """Fetch forecast from Open-Meteo API with daily aggregates in Denver timezone."""
        try:
            # Request daily data only - properly aggregated in America/Denver timezone
            # This ensures snowfall_sum is the true daily total, not hourly values
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,snowfall_sum,precipitation_probability_max,weather_code,wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant",
                "temperature_unit": "fahrenheit",
                "wind_speed_unit": "mph",
                "precipitation_unit": "inch",
                "timezone": "America/Denver",
                "forecast_days": 7
            }
            
            response = requests.get(self.OPEN_METEO_BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error fetching Open-Meteo data: {str(e)}")
            return None
    
    def _parse_open_meteo_forecast(self, forecast_data: Dict[str, Any], resort_name: str, forecast_time: datetime) -> List[Dict[str, Any]]:
        """Parse Open-Meteo daily forecast data into normalized format."""
        forecasts = []
        
        daily = forecast_data.get("daily", {})
        times = daily.get("time", [])
        temp_max = daily.get("temperature_2m_max", [])
        temp_min = daily.get("temperature_2m_min", [])
        precip_sum = daily.get("precipitation_sum", [])
        snowfall_sum = daily.get("snowfall_sum", [])
        precip_prob_max = daily.get("precipitation_probability_max", [])
        weather_code = daily.get("weather_code", [])
        wind_speed_max = daily.get("wind_speed_10m_max", [])
        wind_gust_max = daily.get("wind_gusts_10m_max", [])
        wind_direction = daily.get("wind_direction_10m_dominant", [])
        
        for i, time_str in enumerate(times):
            # Parse date - times come as "YYYY-MM-DD" format
            valid_date = datetime.fromisoformat(time_str)
            
            # Map weather_code to conditions text
            code = weather_code[i] if i < len(weather_code) else None
            conditions_text = self._map_weathercode(code)
            
            forecast = {
                "resort_name": resort_name,
                "source": "OPEN_METEO",
                "forecast_time": forecast_time,
                "valid_time": valid_date,
                "temp_high_f": temp_max[i] if i < len(temp_max) else None,
                "temp_low_f": temp_min[i] if i < len(temp_min) else None,
                "snow_amount_in": snowfall_sum[i] if i < len(snowfall_sum) else None,
                "precip_amount_in": precip_sum[i] if i < len(precip_sum) else None,
                "precip_prob_pct": int(precip_prob_max[i]) if i < len(precip_prob_max) and precip_prob_max[i] is not None else None,
                "wind_speed_mph": wind_speed_max[i] if i < len(wind_speed_max) else None,
                "wind_direction_deg": int(wind_direction[i]) if i < len(wind_direction) and wind_direction[i] is not None else None,
                "wind_gust_mph": wind_gust_max[i] if i < len(wind_gust_max) else None,
                "conditions_text": conditions_text,
                "icon_code": str(code) if code is not None else None,
            }
            
            forecasts.append(forecast)
        
        return forecasts
    
    def _map_weathercode(self, code: Optional[int]) -> str:
        """Map WMO weather code to human-readable conditions."""
        if code is None:
            return "Unknown"
        
        # WMO Weather interpretation codes (WW)
        code_map = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail",
        }
        
        return code_map.get(code, f"Unknown ({code})")
    
    def fetch_all_forecasts(self) -> List[Dict[str, Any]]:
        """Fetch forecasts from Open-Meteo for all resorts."""
        all_forecasts = []
        forecast_time = datetime.now()
        
        print(f"Fetching forecasts for {len(self.resort_coordinates)} resorts...")
        print(f"Forecast time: {forecast_time.isoformat()}")
        print()
        
        for resort_name, coords in self.resort_coordinates.items():
            lat = coords["latitude"]
            lon = coords["longitude"]
            
            print(f"📍 {resort_name} ({lat}, {lon})")
            
            # Fetch Open-Meteo forecast
            print("  Fetching Open-Meteo forecast...")
            om_data = self._fetch_open_meteo_forecast(lat, lon)
            if om_data:
                om_forecasts = self._parse_open_meteo_forecast(om_data, resort_name, forecast_time)
                all_forecasts.extend(om_forecasts)
                print(f"  ✅ Open-Meteo: {len(om_forecasts)} days")
            else:
                print(f"  ⚠️  Open-Meteo: No data")
            
            print()
            time.sleep(0.3)  # Rate limiting
        
        return all_forecasts
    
    def generate_sql_inserts(self, forecasts: List[Dict[str, Any]]) -> str:
        """Generate SQL INSERT statements for forecasts."""
        inserts = []
        
        for forecast in forecasts:
            # Format timestamps
            forecast_time_str = forecast["forecast_time"].strftime("%Y-%m-%d %H:%M:%S")
            valid_time_str = forecast["valid_time"].strftime("%Y-%m-%d %H:%M:%S")
            
            # Build column/value lists
            columns = [
                "resort_name", "source", "forecast_time", "valid_time",
                "temp_high_f", "temp_low_f", "snow_amount_in", "precip_amount_in",
                "precip_prob_pct", "wind_speed_mph", "wind_direction_deg",
                "wind_gust_mph", "conditions_text", "icon_code"
            ]
            
            values = [
                f"'{forecast['resort_name']}'",
                f"'{forecast['source']}'",
                f"'{forecast_time_str}'",
                f"'{valid_time_str}'",
                str(forecast['temp_high_f']) if forecast['temp_high_f'] is not None else "NULL",
                str(forecast['temp_low_f']) if forecast['temp_low_f'] is not None else "NULL",
                str(forecast['snow_amount_in']) if forecast['snow_amount_in'] is not None else "NULL",
                str(forecast['precip_amount_in']) if forecast['precip_amount_in'] is not None else "NULL",
                str(forecast['precip_prob_pct']) if forecast['precip_prob_pct'] is not None else "NULL",
                str(forecast['wind_speed_mph']) if forecast['wind_speed_mph'] is not None else "NULL",
                str(forecast['wind_direction_deg']) if forecast['wind_direction_deg'] is not None else "NULL",
                str(forecast['wind_gust_mph']) if forecast['wind_gust_mph'] is not None else "NULL",
                (f"'{forecast['conditions_text'].replace(chr(39), chr(39) * 2)}'" if forecast['conditions_text'] else "NULL"),
                f"'{forecast['icon_code']}'" if forecast['icon_code'] else "NULL",
            ]
            
            columns_str = ", ".join(columns)
            values_str = ", ".join(values)
            
            # Build upsert statement
            update_cols = [col for col in columns if col not in ["resort_name", "source", "valid_time"]]
            update_clause = ", ".join([f"{col} = EXCLUDED.{col}" for col in update_cols])
            
            insert = f"""INSERT INTO WEATHER_DATA.weather_forecasts ({columns_str})
VALUES ({values_str})
ON CONFLICT (resort_name, source, valid_time) DO UPDATE SET
    {update_clause};"""
            
            inserts.append(insert)
        
        return "\n\n".join(inserts)


def main():
    """Main entry point for testing."""
    collector = ForecastCollector()
    forecasts = collector.fetch_all_forecasts()
    
    print(f"\n✅ Collected {len(forecasts)} forecast records")
    print("\n" + "=" * 60)
    print("GENERATED SQL:")
    print("=" * 60)
    
    sql = collector.generate_sql_inserts(forecasts)
    print(sql)


if __name__ == "__main__":
    main()

