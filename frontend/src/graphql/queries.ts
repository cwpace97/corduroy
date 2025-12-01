import { gql } from '@apollo/client/core';

export const GET_RESORTS = gql`
  query GetResorts {
    resorts {
      location
      totalLifts
      openLifts
      closedLifts
      totalRuns
      openRuns
      closedRuns
      lastUpdated
      lifts {
        liftName
        liftType
        liftStatus
        dateOpened
      }
      runs {
        runName
        runDifficulty
        runStatus
        dateOpened
      }
      liftsHistory {
        date
        openCount
      }
      runsHistory {
        date
        openCount
      }
      recentlyOpenedLifts {
        name
        dateOpened
      }
      recentlyOpenedRuns {
        name
        dateOpened
      }
    }
    globalRecentlyOpened {
      lifts {
        name
        location
        dateOpened
        liftType
        liftCategory
        liftSize
      }
      runs {
        name
        location
        dateOpened
      }
    }
    allResortWeather(days: 7) {
      resortName
      stations {
        stationName
        stationTriplet
        distanceMiles
      }
      trend {
        snowDepthChangeIn
        snowDepthTrend
        tempAvgF
        totalPrecipIn
        latestSnowDepthIn
        snowConditions
      }
      dailyData {
        date
        tempMinF
        tempMaxF
        precipTotalIn
      }
    }
  }
`;

export const GET_RESORTS_SUMMARY = gql`
  query GetResortsSummary {
    resorts {
      location
      openLifts
      totalLifts
      openRuns
      totalRuns
      runsByDifficulty {
        green
        blue
        black
        doubleBlack
        terrainPark
        other
      }
    }
  }
`;

export const GET_ALL_RESORT_WEATHER = gql`
  query GetAllResortWeather($days: Int) {
    allResortWeather(days: $days) {
      resortName
      stations {
        stationName
        stationTriplet
        distanceMiles
      }
      trend {
        snowDepthChangeIn
        snowDepthTrend
        tempAvgF
        totalPrecipIn
        latestSnowDepthIn
        snowConditions
      }
      dailyData {
        date
        snowDepthAvgIn
        snowDepthMaxIn
        tempMinF
        tempMaxF
        precipTotalIn
        windSpeedAvgMph
        windDirectionAvgDeg
        stationData {
          stationName
          stationTriplet
          distanceMiles
          snowDepthAvgIn
        }
      }
      hourlyData {
        date
        hour
        snowDepthIn
        snowWaterEquivalentIn
        tempObservedF
        precipAccumIn
        windSpeedAvgMph
      }
    }
  }
`;

export const GET_RESORT_WEATHER = gql`
  query GetResortWeather($resortName: String!, $days: Int) {
    resortWeather(resortName: $resortName, days: $days) {
      resortName
      stations {
        stationName
        stationTriplet
        distanceMiles
      }
      trend {
        snowDepthChangeIn
        snowDepthTrend
        tempAvgF
        totalPrecipIn
        latestSnowDepthIn
        snowConditions
      }
      dailyData {
        date
        snowDepthAvgIn
        snowDepthMaxIn
        tempMinF
        tempMaxF
        precipTotalIn
        windSpeedAvgMph
        windDirectionAvgDeg
        stationData {
          stationName
          stationTriplet
          distanceMiles
          snowDepthAvgIn
        }
      }
      hourlyData {
        date
        hour
        snowDepthIn
        snowWaterEquivalentIn
        tempObservedF
        precipAccumIn
        windSpeedAvgMph
      }
    }
  }
`;

