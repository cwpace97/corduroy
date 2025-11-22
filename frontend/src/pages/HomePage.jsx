import { useQuery, gql } from '@apollo/client'
import { Link } from 'react-router-dom'
import ResortCard from '../components/ResortCard'
import LoadingSpinner from '../components/LoadingSpinner'
import RecentlyOpened from '../components/RecentlyOpened'

const GET_RESORTS = gql`
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
`

const HomePage = () => {
  const { loading, error, data } = useQuery(GET_RESORTS)

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-red-500/10 border border-red-500 text-red-500 px-6 py-4 rounded-lg">
          <p className="font-semibold">Error loading resort data</p>
          <p className="text-sm mt-1">{error.message}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-7xl mx-auto">
        <header className="mb-12 text-center">
          <h1 className="text-5xl font-bold text-white mb-3">
            ⛷️ Ski Resort Dashboard
          </h1>
          <p className="text-slate-300 text-lg mb-4">
            Real-time lift and trail status for Colorado ski resorts
          </p>
          <Link
            to="/details"
            className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
            View Details Table
          </Link>
        </header>

        {/* Recently Opened Section */}
        <RecentlyOpened data={data?.globalRecentlyOpened} />

        <div className="space-y-6">
          {data?.resorts?.map((resort) => (
            <ResortCard key={resort.location} resort={resort} />
          ))}
        </div>

        {(!data?.resorts || data.resorts.length === 0) && (
          <div className="text-center text-slate-400 mt-12">
            <p className="text-xl">No resort data available</p>
            <p className="mt-2">Run the scrapers to collect data</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default HomePage

