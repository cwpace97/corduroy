#!/usr/bin/env python3
"""GraphQL resolvers for querying ski resort data"""

import psycopg2
import psycopg2.extras
import os
from typing import List, Optional
from .schema import (
    ResortSummary, ResortHomeSummary, Lift, Run, RunsByDifficulty, HistoryDataPoint, 
    RecentlyOpened, GlobalRecentlyOpened, RecentlyOpenedWithLocation,
    WeatherDataPoint, DailyWeatherSummary, WeatherTrend, ResortWeatherSummary,
    StationInfo, StationDailyData, ForecastDataPoint, ResortForecast,
    HourlyTemperaturePoint, DailyHistoricalWeather
)


# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    """Create and return a database connection"""
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def get_all_resorts() -> List[ResortSummary]:
    """Get summary data for all ski resorts"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # Get all unique locations
    cursor.execute("SELECT DISTINCT location FROM SKI_DATA.v_locations ORDER BY location")
    locations = [row['location'] for row in cursor.fetchall()]
    
    resorts = []
    for location in locations:
        resort = get_resort_by_location(location)
        if resort:
            resorts.append(resort)
    
    conn.close()
    return resorts


def get_all_resorts_home() -> List[ResortHomeSummary]:
    """Get pre-aggregated summary data for home page using v_resort_summary view"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cursor.execute("""
        SELECT 
            location,
            total_lifts,
            open_lifts,
            closed_lifts,
            total_runs,
            open_runs,
            closed_runs,
            green_runs,
            blue_runs,
            black_runs,
            double_black_runs,
            terrain_park_runs,
            other_runs,
            last_updated,
            lifts_history,
            runs_history,
            recently_opened_lifts,
            recently_opened_runs
        FROM SKI_DATA.v_resort_summary
        ORDER BY location
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    resorts = []
    for row in rows:
        # Parse JSON arrays from the view
        lifts_history = [
            HistoryDataPoint(date=h['date'], open_count=h['openCount'])
            for h in (row['lifts_history'] or [])
        ]
        runs_history = [
            HistoryDataPoint(date=h['date'], open_count=h['openCount'])
            for h in (row['runs_history'] or [])
        ]
        recently_opened_lifts = [
            RecentlyOpened(name=h['name'], date_opened=h['dateOpened'])
            for h in (row['recently_opened_lifts'] or [])[:3]
        ]
        recently_opened_runs = [
            RecentlyOpened(name=h['name'], date_opened=h['dateOpened'])
            for h in (row['recently_opened_runs'] or [])[:3]
        ]
        
        resorts.append(ResortHomeSummary(
            location=row['location'],
            total_lifts=row['total_lifts'],
            open_lifts=row['open_lifts'],
            closed_lifts=row['closed_lifts'],
            total_runs=row['total_runs'],
            open_runs=row['open_runs'],
            closed_runs=row['closed_runs'],
            runs_by_difficulty=RunsByDifficulty(
                green=row['green_runs'],
                blue=row['blue_runs'],
                black=row['black_runs'],
                double_black=row['double_black_runs'],
                terrain_park=row['terrain_park_runs'],
                other=max(0, row['other_runs'])  # Ensure non-negative
            ),
            last_updated=row['last_updated'] or "Unknown",
            lifts_history=lifts_history,
            runs_history=runs_history,
            recently_opened_lifts=recently_opened_lifts,
            recently_opened_runs=recently_opened_runs
        ))
    
    return resorts


def get_resort_by_location(location: str) -> Optional[ResortSummary]:
    """Get detailed data for a specific resort"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # Get current lifts for this location with date opened
    cursor.execute("""
        SELECT 
            v.lift_name, 
            v.lift_type, 
            v.lift_status, 
            v.updated_date,
            (SELECT MIN(updated_date) 
             FROM SKI_DATA.lifts 
             WHERE location = v.location 
             AND lift_name = v.lift_name 
             AND lift_status = 'true') as date_opened
        FROM SKI_DATA.v_lifts_current v
        WHERE v.location = %s
        ORDER BY v.lift_name
    """, (location,))
    
    lifts_data = cursor.fetchall()
    lifts = []
    open_lifts = 0
    closed_lifts = 0
    last_updated = ""
    
    for row in lifts_data:
        lift_status = "Open" if row['lift_status'] in ['Open', 'open', True, 1, '1', 'true', 'True'] else "Closed"
        lifts.append(Lift(
            lift_name=row['lift_name'],
            lift_type=row['lift_type'] or "Unknown",
            lift_status=lift_status,
            date_opened=row['date_opened'] if lift_status == "Open" else None
        ))
        if lift_status == "Open":
            open_lifts += 1
        else:
            closed_lifts += 1
        
        if row['updated_date'] and (not last_updated or row['updated_date'] > last_updated):
            last_updated = row['updated_date']
    
    # Get current runs for this location with date opened
    cursor.execute("""
        SELECT 
            v.run_name, 
            v.run_difficulty, 
            v.run_status, 
            v.run_area, 
            v.run_groomed, 
            v.updated_date,
            (SELECT MIN(updated_date) 
             FROM SKI_DATA.runs 
             WHERE location = v.location 
             AND run_name = v.run_name 
             AND run_status = 'true') as date_opened
        FROM SKI_DATA.v_runs_current v
        WHERE v.location = %s
        ORDER BY v.run_name
    """, (location,))
    
    runs_data = cursor.fetchall()
    runs = []
    open_runs = 0
    closed_runs = 0
    
    # Track runs by difficulty (open runs only)
    difficulty_counts = {
        'green': 0,
        'blue': 0,
        'black': 0,
        'double_black': 0,
        'terrain_park': 0,
        'other': 0
    }
    
    for row in runs_data:
        run_status = "Open" if row['run_status'] in ['Open', 'open', True, 1, '1', 'true', 'True'] else "Closed"
        difficulty = (row['run_difficulty'] or "Unknown").lower().strip()
        
        runs.append(Run(
            run_name=row['run_name'],
            run_difficulty=row['run_difficulty'] or "Unknown",
            run_status=run_status,
            run_area=row['run_area'],
            run_groomed=bool(row['run_groomed']),
            date_opened=row['date_opened'] if run_status == "Open" else None
        ))
        
        if run_status == "Open":
            open_runs += 1
            
            # Categorize by difficulty
            if 'green' in difficulty or 'easiest' in difficulty or 'beginner' in difficulty:
                difficulty_counts['green'] += 1
            elif 'blue' in difficulty or 'intermediate' in difficulty or 'more difficult' in difficulty:
                difficulty_counts['blue'] += 1
            elif 'double' in difficulty or 'expert' in difficulty or 'most difficult' in difficulty:
                difficulty_counts['double_black'] += 1
            elif 'black' in difficulty or 'advanced' in difficulty or 'difficult' in difficulty:
                difficulty_counts['black'] += 1
            elif 'park' in difficulty or 'terrain' in difficulty:
                difficulty_counts['terrain_park'] += 1
            else:
                difficulty_counts['other'] += 1
        else:
            closed_runs += 1
        
        if row['updated_date'] and (not last_updated or row['updated_date'] > last_updated):
            last_updated = row['updated_date']
    
    # Get lifts history (last 7 days)
    cursor.execute("""
        SELECT updated_date as date, open_count
        FROM SKI_DATA.v_lifts_history
        WHERE location = %s
        ORDER BY updated_date DESC
        LIMIT 7
    """, (location,))
    
    lifts_history_data = cursor.fetchall()
    lifts_history = [
        HistoryDataPoint(date=row['date'], open_count=row['open_count'])
        for row in reversed(lifts_history_data)  # Reverse to show oldest to newest
    ]
    
    # Get runs history (last 7 days)
    cursor.execute("""
        SELECT updated_date as date, open_count
        FROM SKI_DATA.v_runs_history
        WHERE location = %s
        ORDER BY updated_date DESC
        LIMIT 7
    """, (location,))
    
    runs_history_data = cursor.fetchall()
    runs_history = [
        HistoryDataPoint(date=row['date'], open_count=row['open_count'])
        for row in reversed(runs_history_data)  # Reverse to show oldest to newest
    ]
    
    # Get recently opened lifts (top 3)
    cursor.execute("""
        SELECT lift_name, MIN(updated_date) as date_opened
        FROM SKI_DATA.lifts
        WHERE location = %s AND lift_status = 'true'
        GROUP BY lift_name
        ORDER BY date_opened DESC
        LIMIT 3
    """, (location,))
    
    recently_opened_lifts_data = cursor.fetchall()
    recently_opened_lifts = [
        RecentlyOpened(name=row['lift_name'], date_opened=row['date_opened'])
        for row in recently_opened_lifts_data
    ]
    
    # Get recently opened runs (top 3)
    cursor.execute("""
        SELECT run_name, MIN(updated_date) as date_opened
        FROM SKI_DATA.runs
        WHERE location = %s AND run_status = 'true'
        GROUP BY run_name
        ORDER BY date_opened DESC
        LIMIT 3
    """, (location,))
    
    recently_opened_runs_data = cursor.fetchall()
    recently_opened_runs = [
        RecentlyOpened(name=row['run_name'], date_opened=row['date_opened'])
        for row in recently_opened_runs_data
    ]
    
    conn.close()
    
    # Return None if no data found for this location
    if not lifts and not runs:
        return None
    
    return ResortSummary(
        location=location,
        total_lifts=len(lifts),
        open_lifts=open_lifts,
        closed_lifts=closed_lifts,
        total_runs=len(runs),
        open_runs=open_runs,
        closed_runs=closed_runs,
        runs_by_difficulty=RunsByDifficulty(
            green=difficulty_counts['green'],
            blue=difficulty_counts['blue'],
            black=difficulty_counts['black'],
            double_black=difficulty_counts['double_black'],
            terrain_park=difficulty_counts['terrain_park'],
            other=difficulty_counts['other']
        ),
        last_updated=last_updated or "Unknown",
        lifts=lifts,
        runs=runs,
        lifts_history=lifts_history,
        runs_history=runs_history,
        recently_opened_lifts=recently_opened_lifts,
        recently_opened_runs=recently_opened_runs
    )


def get_global_recently_opened() -> GlobalRecentlyOpened:
    """Get recently opened lifts and runs across all resorts"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # Get recently opened lifts across all locations with lift category from mapping table
    cursor.execute("""
        SELECT 
            l.lift_name, 
            l.location, 
            MIN(l.updated_date) as date_opened,
            v.lift_type,
            COALESCE(m.lift_category, 'Unknown') as lift_category,
            m.lift_size
        FROM SKI_DATA.lifts l
        LEFT JOIN SKI_DATA.v_lifts_current v 
            ON l.location = v.location AND l.lift_name = v.lift_name
        LEFT JOIN SKI_DATA.ref__lift_mapping m 
            ON v.lift_type = m.lift_type
        WHERE l.lift_status = 'true'
        GROUP BY l.location, l.lift_name, v.lift_type, m.lift_category, m.lift_size
        ORDER BY date_opened DESC
    """)
    
    lifts_data = cursor.fetchall()
    lifts = [
        RecentlyOpenedWithLocation(
            name=row['lift_name'],
            location=row['location'],
            date_opened=row['date_opened'],
            lift_type=row['lift_type'],
            lift_category=row['lift_category'],
            lift_size=row['lift_size']
        )
        for row in lifts_data
    ]
    
    # Get top 10 recently opened runs across all locations
    cursor.execute("""
        SELECT run_name, location, MIN(updated_date) as date_opened
        FROM SKI_DATA.runs
        WHERE run_status = 'true'
        GROUP BY location, run_name
        ORDER BY date_opened DESC
    """)
    
    runs_data = cursor.fetchall()
    runs = [
        RecentlyOpenedWithLocation(
            name=row['run_name'],
            location=row['location'],
            date_opened=row['date_opened']
        )
        for row in runs_data
    ]
    
    conn.close()
    
    return GlobalRecentlyOpened(lifts=lifts, runs=runs)


def get_resort_weather(resort_name: str, days: int = 7) -> Optional[ResortWeatherSummary]:
    """Get weather summary for a specific resort from all SNOTEL stations with weighted averages"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # Normalize resort name for case-insensitive matching
    resort_name_map = {
        'arapahoe basin': 'Arapahoe Basin',
        'a-basin': 'Arapahoe Basin',
        'copper': 'Copper',
        'copper mountain': 'Copper',
        'loveland': 'Loveland',
        'breckenridge': 'Breckenridge',
        'breck': 'Breckenridge',
        'winter park': 'Winter Park',
        'keystone': 'Keystone',
        'vail': 'Vail',
        'crested butte': 'Crested Butte',
        'steamboat': 'Steamboat',
    }
    
    normalized_name = resort_name_map.get(resort_name.lower(), resort_name)
    
    # Get ALL SNOTEL stations for this resort (up to 3)
    cursor.execute("""
        SELECT 
            rsm.station_triplet, 
            rsm.distance_miles,
            ss.station_name
        FROM WEATHER_DATA.resort_station_mapping rsm
        JOIN WEATHER_DATA.snotel_stations ss ON rsm.station_triplet = ss.station_triplet
        WHERE rsm.resort_name = %s
        ORDER BY rsm.distance_miles ASC
        LIMIT 3
    """, (normalized_name,))
    
    station_rows = cursor.fetchall()
    if not station_rows:
        conn.close()
        return None
    
    # Build station info list
    stations = [
        StationInfo(
            station_name=row['station_name'],
            station_triplet=row['station_triplet'],
            distance_miles=float(row['distance_miles'])
        )
        for row in station_rows
    ]
    
    # Calculate inverse distance weights (closer stations have more weight)
    # Use inverse distance weighting: weight = 1 / distance
    # Add small epsilon to avoid division by zero for very close stations
    epsilon = 0.1
    weights = {}
    total_weight = 0
    for station in stations:
        weight = 1.0 / (station.distance_miles + epsilon)
        weights[station.station_triplet] = weight
        total_weight += weight
    
    # Normalize weights to sum to 1
    for triplet in weights:
        weights[triplet] /= total_weight
    
    # Get daily data for each station
    station_triplets = [s.station_triplet for s in stations]
    triplets_tuple = tuple(station_triplets)
    
    cursor.execute("""
        SELECT 
            station_triplet,
            observation_date::text as date,
            AVG(snow_depth_in) as snow_depth_avg_in,
            MAX(snow_depth_in) as snow_depth_max_in,
            MIN(temp_observed_f) as temp_min_f,
            MAX(temp_observed_f) as temp_max_f,
            MAX(precip_accum_in) - MIN(precip_accum_in) as precip_total_in,
            AVG(wind_speed_avg_mph) as wind_speed_avg_mph,
            AVG(wind_direction_avg_deg) as wind_direction_avg_deg
        FROM WEATHER_DATA.snotel_observations
        WHERE station_triplet IN %s
          AND observation_date >= CURRENT_DATE - INTERVAL '%s days'
        GROUP BY station_triplet, observation_date
        ORDER BY observation_date ASC, station_triplet ASC
    """, (triplets_tuple, days))
    
    daily_rows = cursor.fetchall()
    
    # Organize data by date
    daily_by_date = {}
    for row in daily_rows:
        date = row['date']
        if date not in daily_by_date:
            daily_by_date[date] = {}
        daily_by_date[date][row['station_triplet']] = row
    
    # Build station lookup for names
    station_lookup = {s.station_triplet: s for s in stations}
    
    # Calculate weighted averages for each day
    daily_data = []
    for date in sorted(daily_by_date.keys()):
        date_data = daily_by_date[date]
        
        # Build per-station data for this date
        station_data = []
        for station in stations:
            triplet = station.station_triplet
            if triplet in date_data:
                row = date_data[triplet]
                station_data.append(StationDailyData(
                    station_name=station.station_name,
                    station_triplet=triplet,
                    distance_miles=station.distance_miles,
                    snow_depth_avg_in=float(row['snow_depth_avg_in']) if row['snow_depth_avg_in'] is not None else None,
                ))
        
        # Calculate weighted averages
        def weighted_avg(values_with_triplets):
            """Calculate weighted average from list of (value, triplet) tuples"""
            total = 0.0
            weight_sum = 0.0
            for val, triplet in values_with_triplets:
                if val is not None:
                    # Convert Decimal to float for multiplication
                    total += float(val) * weights[triplet]
                    weight_sum += weights[triplet]
            return total / weight_sum if weight_sum > 0 else None
        
        snow_depths = [(float(date_data[t]['snow_depth_avg_in']), t) for t in date_data if date_data[t]['snow_depth_avg_in'] is not None]
        snow_maxes = [(float(date_data[t]['snow_depth_max_in']), t) for t in date_data if date_data[t]['snow_depth_max_in'] is not None]
        temp_mins = [(float(date_data[t]['temp_min_f']), t) for t in date_data if date_data[t]['temp_min_f'] is not None]
        temp_maxes = [(float(date_data[t]['temp_max_f']), t) for t in date_data if date_data[t]['temp_max_f'] is not None]
        precips = [(float(date_data[t]['precip_total_in']), t) for t in date_data if date_data[t]['precip_total_in'] is not None]
        wind_speeds = [(float(date_data[t]['wind_speed_avg_mph']), t) for t in date_data if date_data[t]['wind_speed_avg_mph'] is not None]
        wind_dirs = [(float(date_data[t]['wind_direction_avg_deg']), t) for t in date_data if date_data[t]['wind_direction_avg_deg'] is not None]
        
        daily_data.append(DailyWeatherSummary(
            date=date,
            snow_depth_avg_in=round(weighted_avg(snow_depths), 1) if snow_depths else None,
            snow_depth_max_in=round(weighted_avg(snow_maxes), 1) if snow_maxes else None,
            temp_min_f=round(weighted_avg(temp_mins), 1) if temp_mins else None,
            temp_max_f=round(weighted_avg(temp_maxes), 1) if temp_maxes else None,
            precip_total_in=round(weighted_avg(precips), 2) if precips else None,
            wind_speed_avg_mph=round(weighted_avg(wind_speeds), 1) if wind_speeds else None,
            wind_direction_avg_deg=round(weighted_avg(wind_dirs)) if wind_dirs else None,
            station_data=station_data,
        ))
    
    # Get hourly data (use weighted average from all stations)
    cursor.execute("""
        SELECT 
            station_triplet,
            observation_date::text as date,
            observation_hour as hour,
            snow_depth_in,
            snow_water_equivalent_in,
            temp_observed_f,
            precip_accum_in,
            wind_speed_avg_mph,
            wind_speed_max_mph
        FROM WEATHER_DATA.snotel_observations
        WHERE station_triplet IN %s
          AND observation_date >= CURRENT_DATE - INTERVAL '%s days'
        ORDER BY observation_date ASC, observation_hour ASC, station_triplet ASC
    """, (triplets_tuple, days))
    
    hourly_rows = cursor.fetchall()
    
    # Organize hourly data by (date, hour)
    hourly_by_datetime = {}
    for row in hourly_rows:
        key = (row['date'], row['hour'])
        if key not in hourly_by_datetime:
            hourly_by_datetime[key] = {}
        hourly_by_datetime[key][row['station_triplet']] = row
    
    # Calculate weighted averages for hourly data
    hourly_data = []
    for (date, hour) in sorted(hourly_by_datetime.keys()):
        datetime_data = hourly_by_datetime[(date, hour)]
        
        def weighted_avg_hourly(field):
            total = 0.0
            weight_sum = 0.0
            for triplet, row in datetime_data.items():
                val = row[field]
                if val is not None:
                    total += float(val) * weights[triplet]
                    weight_sum += weights[triplet]
            return round(total / weight_sum, 1) if weight_sum > 0 else None
        
        hourly_data.append(WeatherDataPoint(
            date=date,
            hour=hour,
            snow_depth_in=weighted_avg_hourly('snow_depth_in'),
            snow_water_equivalent_in=weighted_avg_hourly('snow_water_equivalent_in'),
            temp_observed_f=weighted_avg_hourly('temp_observed_f'),
            precip_accum_in=weighted_avg_hourly('precip_accum_in'),
            wind_speed_avg_mph=weighted_avg_hourly('wind_speed_avg_mph'),
            wind_speed_max_mph=weighted_avg_hourly('wind_speed_max_mph'),
        ))
    
    # Get daily aggregated historical weather from the view (much smaller response)
    cursor.execute("""
        SELECT 
            observation_date::text as date,
            temp_min_f,
            temp_max_f,
            temp_avg_f,
            precip_total_in,
            snowfall_total_in
        FROM WEATHER_DATA.historical_weather_daily
        WHERE resort_name = %s
          AND observation_date >= CURRENT_DATE - INTERVAL '%s days'
        ORDER BY observation_date ASC
    """, (normalized_name, days))
    
    daily_weather_rows = cursor.fetchall()
    historical_weather = [
        DailyHistoricalWeather(
            date=row['date'],
            temp_min_f=float(row['temp_min_f']) if row['temp_min_f'] is not None else None,
            temp_max_f=float(row['temp_max_f']) if row['temp_max_f'] is not None else None,
            temp_avg_f=float(row['temp_avg_f']) if row['temp_avg_f'] is not None else None,
            precip_total_in=float(row['precip_total_in']) if row['precip_total_in'] is not None else None,
            snowfall_total_in=float(row['snowfall_total_in']) if row['snowfall_total_in'] is not None else None,
        )
        for row in daily_weather_rows
    ]
    
    # Keep hourly_temperature empty for backward compatibility (deprecated)
    hourly_temperature: List[HourlyTemperaturePoint] = []
    
    # Update daily_data with snowfall totals from historical_weather
    daily_snowfall = {row['date']: float(row['snowfall_total_in']) if row['snowfall_total_in'] else 0 for row in daily_weather_rows}
    for d in daily_data:
        if d.date in daily_snowfall:
            d.snowfall_total_in = round(daily_snowfall[d.date], 2)
    
    # Calculate trend based on weighted daily data
    trend = _calculate_weather_trend(daily_data, hourly_data)
    
    conn.close()
    
    return ResortWeatherSummary(
        resort_name=normalized_name,
        stations=stations,
        trend=trend,
        daily_data=daily_data,
        hourly_data=hourly_data,
        hourly_temperature=hourly_temperature,
        historical_weather=historical_weather,
    )


def _calculate_weather_trend(daily_data: List[DailyWeatherSummary], hourly_data: List[WeatherDataPoint]) -> WeatherTrend:
    """Calculate weather trend from daily and hourly data"""
    
    # Get snow depth values that are not None
    snow_depths = [d.snow_depth_avg_in for d in daily_data if d.snow_depth_avg_in is not None]
    
    # Calculate snow depth change
    if len(snow_depths) >= 2:
        first_half = snow_depths[:len(snow_depths)//2]
        second_half = snow_depths[len(snow_depths)//2:]
        first_avg = sum(first_half) / len(first_half) if first_half else 0
        second_avg = sum(second_half) / len(second_half) if second_half else 0
        snow_depth_change = second_avg - first_avg
    else:
        snow_depth_change = 0.0
    
    # Determine trend direction
    if snow_depth_change > 1.0:
        snow_depth_trend = "increasing"
    elif snow_depth_change < -1.0:
        snow_depth_trend = "decreasing"
    else:
        snow_depth_trend = "stable"
    
    # Calculate average temperature
    temps = [d.temp_max_f for d in daily_data if d.temp_max_f is not None]
    temps += [d.temp_min_f for d in daily_data if d.temp_min_f is not None]
    temp_avg = sum(temps) / len(temps) if temps else None
    
    # Calculate total precipitation
    precips = [d.precip_total_in for d in daily_data if d.precip_total_in is not None]
    total_precip = sum(precips) if precips else 0.0
    
    # Get latest snow depth
    latest_snow_depth = snow_depths[-1] if snow_depths else None
    
    # Determine snow conditions based on snow depth and trend
    if latest_snow_depth is None:
        snow_conditions = "unknown"
    elif latest_snow_depth >= 40 and snow_depth_trend != "decreasing":
        snow_conditions = "excellent"
    elif latest_snow_depth >= 25 or (latest_snow_depth >= 15 and snow_depth_trend == "increasing"):
        snow_conditions = "good"
    elif latest_snow_depth >= 10:
        snow_conditions = "fair"
    else:
        snow_conditions = "poor"
    
    return WeatherTrend(
        snow_depth_change_in=round(snow_depth_change, 1),
        snow_depth_trend=snow_depth_trend,
        temp_avg_f=round(temp_avg, 1) if temp_avg is not None else None,
        total_precip_in=round(total_precip, 2),
        latest_snow_depth_in=round(latest_snow_depth, 1) if latest_snow_depth is not None else None,
        snow_conditions=snow_conditions,
    )


def get_all_resort_weather(days: int = 7) -> List[ResortWeatherSummary]:
    """Get weather summaries for all resorts"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # Get all unique resort names from the mapping
    cursor.execute("""
        SELECT DISTINCT resort_name
        FROM WEATHER_DATA.resort_station_mapping
        ORDER BY resort_name
    """)
    
    resort_names = [row['resort_name'] for row in cursor.fetchall()]
    conn.close()
    
    # Get weather for each resort
    weather_summaries = []
    for resort_name in resort_names:
        weather = get_resort_weather(resort_name, days)
        if weather:
            weather_summaries.append(weather)
    
    return weather_summaries


def get_resort_forecast(resort_name: str, days: int = 7) -> Optional[ResortForecast]:
    """Get weather forecast for a specific resort from multiple sources"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # Normalize resort name for case-insensitive matching
    resort_name_map = {
        'arapahoe basin': 'Arapahoe Basin',
        'a-basin': 'Arapahoe Basin',
        'copper': 'Copper',
        'copper mountain': 'Copper',
        'loveland': 'Loveland',
        'breckenridge': 'Breckenridge',
        'breck': 'Breckenridge',
        'winter park': 'Winter Park',
        'keystone': 'Keystone',
        'vail': 'Vail',
        'crested butte': 'Crested Butte',
        'steamboat': 'Steamboat',
        'purgatory': 'Purgatory',
        'telluride': 'Telluride',
    }
    
    normalized_name = resort_name_map.get(resort_name.lower(), resort_name)
    
    # Get forecasts from all sources (use CURRENT_DATE to include today's forecast)
    cursor.execute("""
        SELECT 
            source,
            forecast_time::text as forecast_time,
            valid_time::text as valid_time,
            temp_high_f,
            temp_low_f,
            snow_amount_in,
            precip_amount_in,
            precip_prob_pct,
            wind_speed_mph,
            wind_direction_deg,
            wind_gust_mph,
            conditions_text,
            icon_code
        FROM WEATHER_DATA.weather_forecasts
        WHERE resort_name = %s
          AND valid_time >= CURRENT_DATE
          AND valid_time <= CURRENT_DATE + INTERVAL '%s days'
        ORDER BY source, valid_time ASC
    """, (normalized_name, days))
    
    forecast_rows = cursor.fetchall()
    conn.close()
    
    if not forecast_rows:
        return None
    
    forecasts = [
        ForecastDataPoint(
            source=row['source'],
            forecast_time=row['forecast_time'],
            valid_time=row['valid_time'],
            temp_high_f=float(row['temp_high_f']) if row['temp_high_f'] is not None else None,
            temp_low_f=float(row['temp_low_f']) if row['temp_low_f'] is not None else None,
            snow_amount_in=float(row['snow_amount_in']) if row['snow_amount_in'] is not None else None,
            precip_amount_in=float(row['precip_amount_in']) if row['precip_amount_in'] is not None else None,
            precip_prob_pct=int(row['precip_prob_pct']) if row['precip_prob_pct'] is not None else None,
            wind_speed_mph=float(row['wind_speed_mph']) if row['wind_speed_mph'] is not None else None,
            wind_direction_deg=int(row['wind_direction_deg']) if row['wind_direction_deg'] is not None else None,
            wind_gust_mph=float(row['wind_gust_mph']) if row['wind_gust_mph'] is not None else None,
            conditions_text=row['conditions_text'],
            icon_code=row['icon_code'],
        )
        for row in forecast_rows
    ]
    
    return ResortForecast(
        resort_name=normalized_name,
        forecasts=forecasts
    )


def get_all_resort_forecasts(days: int = 7) -> List[ResortForecast]:
    """Get weather forecasts for all resorts"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # Get all unique resort names from forecasts (use CURRENT_DATE to include today)
    cursor.execute("""
        SELECT DISTINCT resort_name
        FROM WEATHER_DATA.weather_forecasts
        WHERE valid_time >= CURRENT_DATE
        ORDER BY resort_name
    """)
    
    resort_names = [row['resort_name'] for row in cursor.fetchall()]
    conn.close()
    
    # Get forecasts for each resort
    forecast_summaries = []
    for resort_name in resort_names:
        forecast = get_resort_forecast(resort_name, days)
        if forecast:
            forecast_summaries.append(forecast)
    
    return forecast_summaries

