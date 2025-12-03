import { gql } from '@apollo/client/core';

// Home page query - uses pre-aggregated view (no individual lifts/runs)
export const GET_RESORTS_HOME = gql`
  query GetResortsHome {
    resortsHome {
      location
      totalLifts
      openLifts
      closedLifts
      totalRuns
      openRuns
      closedRuns
      lastUpdated
      runsByDifficulty {
        green
        blue
        black
        doubleBlack
        terrainPark
        other
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
        snowfallTotalIn
      }
      historicalWeather {
        date
        tempMinF
        tempMaxF
        snowfallTotalIn
      }
    }
    allResortForecasts(days: 7) {
      resortName
      forecasts {
        validTime
        tempHighF
        tempLowF
        snowAmountIn
      }
    }
  }
`;

// Full resort details query - includes individual lifts/runs (for detail pages)
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
        snowfallTotalIn
      }
      historicalWeather {
        date
        tempMinF
        tempMaxF
        snowfallTotalIn
      }
    }
    allResortForecasts(days: 7) {
      resortName
      forecasts {
        validTime
        tempHighF
        tempLowF
        snowAmountIn
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
        snowfallTotalIn
        windSpeedAvgMph
        windDirectionAvgDeg
        stationData {
          stationName
          stationTriplet
          distanceMiles
          snowDepthAvgIn
        }
      }
      historicalWeather {
        date
        tempMinF
        tempMaxF
        tempAvgF
        precipTotalIn
        snowfallTotalIn
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
        snowfallTotalIn
        windSpeedAvgMph
        windDirectionAvgDeg
        stationData {
          stationName
          stationTriplet
          distanceMiles
          snowDepthAvgIn
        }
      }
      historicalWeather {
        date
        tempMinF
        tempMaxF
        tempAvgF
        precipTotalIn
        snowfallTotalIn
      }
    }
  }
`;

export const GET_RESORT_FORECAST = gql`
  query GetResortForecast($resortName: String!, $days: Int) {
    resortForecast(resortName: $resortName, days: $days) {
      resortName
      forecasts {
        source
        forecastTime
        validTime
        tempHighF
        tempLowF
        snowAmountIn
        precipAmountIn
        precipProbPct
        windSpeedMph
        windDirectionDeg
        windGustMph
        conditionsText
        iconCode
      }
    }
  }
`;

export const GET_ALL_RESORT_FORECASTS = gql`
  query GetAllResortForecasts($days: Int) {
    allResortForecasts(days: $days) {
      resortName
      forecasts {
        source
        forecastTime
        validTime
        tempHighF
        tempLowF
        snowAmountIn
        precipAmountIn
        precipProbPct
        windSpeedMph
        windDirectionDeg
        windGustMph
        conditionsText
        iconCode
      }
    }
  }
`;

