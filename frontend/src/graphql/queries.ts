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
      }
      runs {
        name
        location
        dateOpened
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

