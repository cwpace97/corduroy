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

