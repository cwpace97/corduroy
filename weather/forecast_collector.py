#!/usr/bin/env python3
"""
Weather Forecast Collector

Fetches weather forecasts from NWS API and Open-Meteo API for Colorado ski resorts.
Normalizes the data into a common schema and generates SQL INSERT statements.
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import os
import time


class ForecastCollector:
    """Collects weather forecasts from multiple sources for ski resorts."""
    
    NWS_BASE_URL = "https://api.weather.gov"
    OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"
    
    def __init__(self, mapping_file: str = "resort_snotel_mapping.json"):
        """
        Initialize the collector with resort coordinates.
        
        Args:
            mapping_file: Path to the JSON file containing resort coordinates
        """
        self.mapping_file = mapping_file
        self.resort_coordinates = self._load_resort_coordinates()
        self.user_agent = "CorduroyWeatherApp/1.0 (https://github.com/yourusername/corduroy)"
    
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
    
    def _get_nws_grid_point(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Get NWS grid point for a given lat/lon.
        NWS requires a two-step process: lat/lon -> grid point -> forecast.
        """
        try:
            # Step 1: Get grid point
            points_url = f"{self.NWS_BASE_URL}/points/{latitude:.4f},{longitude:.4f}"
            headers = {"User-Agent": self.user_agent, "Accept": "application/json"}
            
            response = requests.get(points_url, headers=headers, timeout=10)
            response.raise_for_status()
            points_data = response.json()
            
            # Extract forecast URL from properties
            forecast_url = points_data.get("properties", {}).get("forecast")
            if not forecast_url:
                print(f"  ⚠️  No forecast URL found for {latitude},{longitude}")
                return None
            
            # Step 2: Get forecast
            forecast_response = requests.get(forecast_url, headers=headers, timeout=10)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()
            
            return forecast_data
            
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error fetching NWS data: {str(e)}")
            return None
    
    def _parse_nws_forecast(self, forecast_data: Dict[str, Any], resort_name: str, forecast_time: datetime) -> List[Dict[str, Any]]:
        """Parse NWS forecast data into normalized format."""
        forecasts = []
        
        periods = forecast_data.get("properties", {}).get("periods", [])
        
        for period in periods:
            # NWS provides day/night periods, we'll use both
            valid_start = datetime.fromisoformat(period["startTime"].replace("Z", "+00:00"))
            
            # Extract temperature
            temp_high = period.get("temperature")
            temp_low = None
            
            # NWS provides isDaytime flag - use high temp for day, low for night
            if period.get("isDaytime"):
                temp_high = period.get("temperature")
            else:
                temp_low = period.get("temperature")
            
            # Extract wind
            wind_speed_str = period.get("windSpeed", "")
            wind_speed = self._parse_wind_speed(wind_speed_str)
            wind_direction_str = period.get("windDirection", "")
            wind_direction = self._parse_wind_direction(wind_direction_str)
            
            # Extract precipitation probability
            precip_prob = period.get("probabilityOfPrecipitation", {}).get("value")
            
            # Extract conditions
            conditions = period.get("shortForecast", "")
            icon = period.get("icon", "")
            
            # Try to extract snow amount from detailed forecast
            detailed_forecast = period.get("detailedForecast", "")
            snow_amount = self._extract_snow_amount(detailed_forecast)
            
            forecast = {
                "resort_name": resort_name,
                "source": "NWS",
                "forecast_time": forecast_time,
                "valid_time": valid_start,
                "temp_high_f": temp_high,
                "temp_low_f": temp_low,
                "snow_amount_in": snow_amount,
                "precip_amount_in": None,  # NWS doesn't provide this directly
                "precip_prob_pct": precip_prob,
                "wind_speed_mph": wind_speed,
                "wind_direction_deg": wind_direction,
                "wind_gust_mph": None,
                "conditions_text": conditions,
                "icon_code": icon,
            }
            
            forecasts.append(forecast)
        
        return forecasts
    
    def _fetch_open_meteo_forecast(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """Fetch forecast from Open-Meteo API."""
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "hourly": "temperature_2m,precipitation_probability,precipitation,snowfall,weathercode,windspeed_10m,winddirection_10m,windgusts_10m",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,snowfall_sum,precipitation_probability_max,weathercode",
                "temperature_unit": "fahrenheit",
                "windspeed_unit": "mph",
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
        """Parse Open-Meteo forecast data into normalized format."""
        forecasts = []
        
        daily = forecast_data.get("daily", {})
        times = daily.get("time", [])
        temp_max = daily.get("temperature_2m_max", [])
        temp_min = daily.get("temperature_2m_min", [])
        precip_sum = daily.get("precipitation_sum", [])
        snowfall_sum = daily.get("snowfall_sum", [])
        precip_prob_max = daily.get("precipitation_probability_max", [])
        weathercode = daily.get("weathercode", [])
        
        # Get hourly data for wind (use average for the day)
        hourly = forecast_data.get("hourly", {})
        hourly_times = hourly.get("time", [])
        hourly_windspeed = hourly.get("windspeed_10m", [])
        hourly_winddir = hourly.get("winddirection_10m", [])
        hourly_windgusts = hourly.get("windgusts_10m", [])
        
        for i, time_str in enumerate(times):
            # Parse date
            valid_date = datetime.fromisoformat(time_str.replace("T00:00", ""))
            
            # Calculate average wind for this day from hourly data
            day_start_idx = None
            day_end_idx = None
            for j, ht in enumerate(hourly_times):
                ht_date = datetime.fromisoformat(ht.replace("T", " "))
                if ht_date.date() == valid_date.date():
                    if day_start_idx is None:
                        day_start_idx = j
                    day_end_idx = j
            
            wind_speed = None
            wind_direction = None
            wind_gust = None
            if day_start_idx is not None and day_end_idx is not None:
                day_winds = hourly_windspeed[day_start_idx:day_end_idx+1]
                day_winddirs = hourly_winddir[day_start_idx:day_end_idx+1]
                day_gusts = hourly_windgusts[day_start_idx:day_end_idx+1]
                
                wind_speed = sum(day_winds) / len(day_winds) if day_winds else None
                wind_direction = self._calculate_average_wind_direction(day_winddirs) if day_winddirs else None
                wind_gust = max(day_gusts) if day_gusts else None
            
            # Map weathercode to conditions text
            conditions_text = self._map_weathercode(weathercode[i] if i < len(weathercode) else None)
            
            forecast = {
                "resort_name": resort_name,
                "source": "OPEN_METEO",
                "forecast_time": forecast_time,
                "valid_time": valid_date,
                "temp_high_f": temp_max[i] if i < len(temp_max) else None,
                "temp_low_f": temp_min[i] if i < len(temp_min) else None,
                "snow_amount_in": snowfall_sum[i] if i < len(snowfall_sum) else None,
                "precip_amount_in": precip_sum[i] if i < len(precip_sum) else None,
                "precip_prob_pct": int(precip_prob_max[i]) if i < len(precip_prob_max) else None,
                "wind_speed_mph": wind_speed,
                "wind_direction_deg": int(wind_direction) if wind_direction else None,
                "wind_gust_mph": wind_gust,
                "conditions_text": conditions_text,
                "icon_code": str(weathercode[i]) if i < len(weathercode) else None,
            }
            
            forecasts.append(forecast)
        
        return forecasts
    
    def _parse_wind_speed(self, wind_speed_str: str) -> Optional[float]:
        """Parse wind speed string like '5 to 10 mph' or '10 mph'."""
        if not wind_speed_str:
            return None
        
        try:
            # Extract numbers from string
            import re
            numbers = re.findall(r'\d+', wind_speed_str)
            if numbers:
                # Take the average if range, or single value
                if len(numbers) >= 2:
                    return (float(numbers[0]) + float(numbers[1])) / 2
                else:
                    return float(numbers[0])
        except:
            pass
        
        return None
    
    def _parse_wind_direction(self, wind_direction_str: str) -> Optional[int]:
        """Parse wind direction string like 'N' or 'NW' to degrees."""
        if not wind_direction_str:
            return None
        
        direction_map = {
            "N": 0, "NNE": 22, "NE": 45, "ENE": 67,
            "E": 90, "ESE": 112, "SE": 135, "SSE": 157,
            "S": 180, "SSW": 202, "SW": 225, "WSW": 247,
            "W": 270, "WNW": 292, "NW": 315, "NNW": 337
        }
        
        return direction_map.get(wind_direction_str.upper())
    
    def _extract_snow_amount(self, detailed_forecast: str) -> Optional[float]:
        """Extract snow amount in inches from detailed forecast text."""
        if not detailed_forecast:
            return None
        
        import re
        # Look for patterns like "1 to 3 inches" or "2 inches"
        patterns = [
            r'(\d+(?:\.\d+)?)\s*to\s*(\d+(?:\.\d+)?)\s*inch',
            r'(\d+(?:\.\d+)?)\s*inch',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, detailed_forecast.lower())
            if match:
                if len(match.groups()) == 2:
                    # Range - take average
                    return (float(match.group(1)) + float(match.group(2))) / 2
                else:
                    return float(match.group(1))
        
        return None
    
    def _calculate_average_wind_direction(self, directions: List[float]) -> float:
        """Calculate average wind direction (handles circular nature of degrees)."""
        if not directions:
            return None
        
        import math
        sin_sum = sum(math.sin(math.radians(d)) for d in directions)
        cos_sum = sum(math.cos(math.radians(d)) for d in directions)
        
        avg_rad = math.atan2(sin_sum / len(directions), cos_sum / len(directions))
        avg_deg = math.degrees(avg_rad)
        
        return avg_deg if avg_deg >= 0 else avg_deg + 360
    
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
        """Fetch forecasts from all sources for all resorts."""
        all_forecasts = []
        forecast_time = datetime.now()
        
        print(f"Fetching forecasts for {len(self.resort_coordinates)} resorts...")
        print(f"Forecast time: {forecast_time.isoformat()}")
        print()
        
        for resort_name, coords in self.resort_coordinates.items():
            lat = coords["latitude"]
            lon = coords["longitude"]
            
            print(f"📍 {resort_name} ({lat}, {lon})")
            
            # Fetch NWS forecast
            print("  Fetching NWS forecast...")
            nws_data = self._get_nws_grid_point(lat, lon)
            if nws_data:
                nws_forecasts = self._parse_nws_forecast(nws_data, resort_name, forecast_time)
                all_forecasts.extend(nws_forecasts)
                print(f"  ✅ NWS: {len(nws_forecasts)} periods")
            else:
                print(f"  ⚠️  NWS: No data")
            
            # Small delay to be respectful to APIs
            time.sleep(0.5)
            
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
            time.sleep(0.5)  # Rate limiting
        
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

