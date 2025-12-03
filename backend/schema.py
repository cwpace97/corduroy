#!/usr/bin/env python3
"""GraphQL schema definitions for ski resort data"""

import strawberry
from typing import List, Optional


@strawberry.type
class Run:
    """Ski run/trail information"""
    run_name: str
    run_difficulty: str
    run_status: str
    run_area: Optional[str] = None
    run_groomed: bool = False
    date_opened: Optional[str] = None


@strawberry.type
class Lift:
    """Ski lift information"""
    lift_name: str
    lift_type: str
    lift_status: str
    date_opened: Optional[str] = None


@strawberry.type
class RunsByDifficulty:
    """Runs grouped by difficulty level"""
    green: int = 0
    blue: int = 0
    black: int = 0
    double_black: int = 0
    terrain_park: int = 0
    other: int = 0


@strawberry.type
class HistoryDataPoint:
    """Historical data point for charts"""
    date: str
    open_count: int


@strawberry.type
class RecentlyOpened:
    """Recently opened lift or run information"""
    name: str
    date_opened: str


@strawberry.type
class RecentlyOpenedWithLocation:
    """Recently opened lift or run with location information"""
    name: str
    location: str
    date_opened: str
    lift_type: Optional[str] = None
    lift_category: Optional[str] = None
    lift_size: Optional[int] = None


@strawberry.type
class ResortSummary:
    """Summary information for a ski resort"""
    location: str
    total_lifts: int
    open_lifts: int
    closed_lifts: int
    total_runs: int
    open_runs: int
    closed_runs: int
    runs_by_difficulty: RunsByDifficulty
    last_updated: str
    lifts: List[Lift]
    runs: List[Run]
    lifts_history: List[HistoryDataPoint]
    runs_history: List[HistoryDataPoint]
    recently_opened_lifts: List[RecentlyOpened]
    recently_opened_runs: List[RecentlyOpened]


@strawberry.type
class GlobalRecentlyOpened:
    """Global recently opened lifts and runs across all resorts"""
    lifts: List[RecentlyOpenedWithLocation]
    runs: List[RecentlyOpenedWithLocation]


@strawberry.type
class WeatherDataPoint:
    """Single weather observation data point"""
    date: str
    hour: Optional[int] = None
    snow_depth_in: Optional[float] = None
    snow_water_equivalent_in: Optional[float] = None
    temp_observed_f: Optional[float] = None
    temp_min_f: Optional[float] = None
    temp_max_f: Optional[float] = None
    precip_accum_in: Optional[float] = None
    wind_speed_avg_mph: Optional[float] = None
    wind_speed_max_mph: Optional[float] = None


@strawberry.type
class HourlyTemperaturePoint:
    """Hourly temperature observation from Open-Meteo"""
    date: str
    hour: int
    temperature_f: Optional[float] = None
    precipitation_in: Optional[float] = None
    snowfall_in: Optional[float] = None


@strawberry.type
class DailyHistoricalWeather:
    """Daily aggregated historical weather from Open-Meteo"""
    date: str
    temp_min_f: Optional[float] = None
    temp_max_f: Optional[float] = None
    temp_avg_f: Optional[float] = None
    precip_total_in: Optional[float] = None
    snowfall_total_in: Optional[float] = None


@strawberry.type
class StationDailyData:
    """Daily data for a single SNOTEL station"""
    station_name: str
    station_triplet: str
    distance_miles: float
    snow_depth_avg_in: Optional[float] = None


@strawberry.type
class DailyWeatherSummary:
    """Daily aggregated weather data with weighted averages and per-station data"""
    date: str
    # Weighted average values (based on inverse distance)
    snow_depth_avg_in: Optional[float] = None
    snow_depth_max_in: Optional[float] = None
    temp_min_f: Optional[float] = None
    temp_max_f: Optional[float] = None
    precip_total_in: Optional[float] = None
    snowfall_total_in: Optional[float] = None
    wind_speed_avg_mph: Optional[float] = None
    wind_direction_avg_deg: Optional[int] = None
    # Per-station snow depth data for charting
    station_data: List[StationDailyData] = strawberry.field(default_factory=list)


@strawberry.type
class StationInfo:
    """Information about a SNOTEL station"""
    station_name: str
    station_triplet: str
    distance_miles: float


@strawberry.type
class WeatherTrend:
    """Weather trend analysis for a resort"""
    snow_depth_change_in: float  # Change over period (positive = gaining snow)
    snow_depth_trend: str  # "increasing", "decreasing", "stable"
    temp_avg_f: Optional[float] = None
    total_precip_in: float
    latest_snow_depth_in: Optional[float] = None
    snow_conditions: str  # "excellent", "good", "fair", "poor"


@strawberry.type
class ResortWeatherSummary:
    """Complete weather summary for a resort"""
    resort_name: str
    stations: List[StationInfo]  # All SNOTEL stations for this resort
    trend: WeatherTrend
    daily_data: List[DailyWeatherSummary]
    hourly_data: List[WeatherDataPoint]
    hourly_temperature: List[HourlyTemperaturePoint]  # Hourly temps from Open-Meteo (deprecated, use historical_weather)
    historical_weather: List[DailyHistoricalWeather]  # Daily aggregated weather from Open-Meteo


@strawberry.type
class ForecastDataPoint:
    """Single forecast data point from a source"""
    source: str  # 'OPEN_METEO'
    forecast_time: str  # When forecast was generated
    valid_time: str  # When forecast is valid for
    temp_high_f: Optional[float] = None
    temp_low_f: Optional[float] = None
    snow_amount_in: Optional[float] = None
    precip_amount_in: Optional[float] = None
    precip_prob_pct: Optional[int] = None
    wind_speed_mph: Optional[float] = None
    wind_direction_deg: Optional[int] = None
    wind_gust_mph: Optional[float] = None
    conditions_text: Optional[str] = None
    icon_code: Optional[str] = None


@strawberry.type
class ResortForecast:
    """Weather forecast for a resort with multiple sources"""
    resort_name: str
    forecasts: List[ForecastDataPoint]  # Forecasts from all sources


@strawberry.type
class Query:
    """GraphQL query root"""
    
    @strawberry.field
    def resorts(self) -> List[ResortSummary]:
        """Get summary data for all ski resorts"""
        from .resolvers import get_all_resorts
        return get_all_resorts()
    
    @strawberry.field
    def resort(self, location: str) -> Optional[ResortSummary]:
        """Get detailed data for a specific resort"""
        from .resolvers import get_resort_by_location
        return get_resort_by_location(location)
    
    @strawberry.field
    def global_recently_opened(self) -> GlobalRecentlyOpened:
        """Get recently opened lifts and runs across all resorts"""
        from .resolvers import get_global_recently_opened
        return get_global_recently_opened()
    
    @strawberry.field
    def resort_weather(self, resort_name: str, days: int = 7) -> Optional[ResortWeatherSummary]:
        """Get weather summary for a specific resort"""
        from .resolvers import get_resort_weather
        return get_resort_weather(resort_name, days)
    
    @strawberry.field
    def all_resort_weather(self, days: int = 7) -> List[ResortWeatherSummary]:
        """Get weather summaries for all resorts"""
        from .resolvers import get_all_resort_weather
        return get_all_resort_weather(days)
    
    @strawberry.field
    def resort_forecast(self, resort_name: str, days: int = 7) -> Optional[ResortForecast]:
        """Get weather forecast for a specific resort from multiple sources"""
        from .resolvers import get_resort_forecast
        return get_resort_forecast(resort_name, days)
    
    @strawberry.field
    def all_resort_forecasts(self, days: int = 7) -> List[ResortForecast]:
        """Get weather forecasts for all resorts from multiple sources"""
        from .resolvers import get_all_resort_forecasts
        return get_all_resort_forecasts(days)

