import { useQuery, gql } from '@apollo/client'
import { Link } from 'react-router-dom'
import { useState } from 'react'
import LoadingSpinner from '../components/LoadingSpinner'

const GET_RESORTS_SUMMARY = gql`
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
`

const DetailsPage = () => {
  const { loading, error, data } = useQuery(GET_RESORTS_SUMMARY)
  const [sortBy, setSortBy] = useState(null)
  const [sortDirection, setSortDirection] = useState('asc') // 'asc' or 'desc'

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

  const getStatusColor = (resort) => {
    if (resort.openLifts === 0) return 'bg-red-500'
    return 'bg-green-500'
  }

  const getTotalOpenByDifficulty = (resort) => {
    const difficulty = resort.runsByDifficulty
    return (
      difficulty.green +
      difficulty.blue +
      difficulty.black +
      difficulty.doubleBlack +
      difficulty.terrainPark +
      difficulty.other
    )
  }

  const handleSort = (type) => {
    if (sortBy === type) {
      if (sortDirection === 'asc') {
        setSortDirection('desc')
      } else {
        // Turn off sorting
        setSortBy(null)
        setSortDirection('asc')
      }
    } else {
      setSortBy(type)
      // For numeric sorts (lifts/runs), start with descending (highest first)
      // For name sort, start with ascending (A-Z)
      const initialDirection = type === 'name' ? 'asc' : 'desc'
      setSortDirection(initialDirection)
    }
  }

  const getSortedResorts = () => {
    if (!data?.resorts) return []
    
    const resortsCopy = [...data.resorts]
    
    if (!sortBy) return resortsCopy
    
    return resortsCopy.sort((a, b) => {
      let compareValue = 0
      
      switch (sortBy) {
        case 'name':
          compareValue = a.location.localeCompare(b.location)
          break
        case 'liftsOpen':
          compareValue = a.openLifts - b.openLifts
          break
        case 'liftsOpenPercent':
          const aLiftsPercent = a.totalLifts > 0 ? (a.openLifts / a.totalLifts) * 100 : 0
          const bLiftsPercent = b.totalLifts > 0 ? (b.openLifts / b.totalLifts) * 100 : 0
          compareValue = aLiftsPercent - bLiftsPercent
          break
        case 'runsOpen':
          compareValue = a.openRuns - b.openRuns
          break
        case 'runsOpenPercent':
          const aRunsPercent = a.totalRuns > 0 ? (a.openRuns / a.totalRuns) * 100 : 0
          const bRunsPercent = b.totalRuns > 0 ? (b.openRuns / b.totalRuns) * 100 : 0
          compareValue = aRunsPercent - bRunsPercent
          break
        default:
          return 0
      }
      
      return sortDirection === 'asc' ? compareValue : -compareValue
    })
  }

  const getSortButtonClass = (type) => {
    const baseClasses = 'px-4 py-2 rounded-lg font-medium text-sm transition-colors'
    if (sortBy === type) {
      return `${baseClasses} bg-blue-600 text-white`
    }
    return `${baseClasses} bg-gray-300 text-gray-700 hover:bg-gray-400`
  }

  const getSortIcon = (type) => {
    if (sortBy !== type) return null
    if (sortDirection === 'asc') {
      return ' ↑'
    }
    return ' ↓'
  }

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <Link
            to="/"
            className="inline-flex items-center text-slate-300 hover:text-white transition-colors mb-4"
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
                d="M10 19l-7-7m0 0l7-7m-7 7h18"
              />
            </svg>
            Back to Dashboard
          </Link>
          <h1 className="text-4xl font-bold text-white mb-2">
            Resort Details
          </h1>
          <p className="text-slate-300">
            Condensed view of all resort information
          </p>
        </header>

        <div className="mb-4 flex flex-wrap gap-2">
          <button
            onClick={() => handleSort('name')}
            className={getSortButtonClass('name')}
          >
            Sort by Name{getSortIcon('name')}
          </button>
          <button
            onClick={() => handleSort('liftsOpen')}
            className={getSortButtonClass('liftsOpen')}
          >
            Sort by Lifts Open{getSortIcon('liftsOpen')}
          </button>
          <button
            onClick={() => handleSort('liftsOpenPercent')}
            className={getSortButtonClass('liftsOpenPercent')}
          >
            Sort by Lifts Open %{getSortIcon('liftsOpenPercent')}
          </button>
          <button
            onClick={() => handleSort('runsOpen')}
            className={getSortButtonClass('runsOpen')}
          >
            Sort by Runs Open{getSortIcon('runsOpen')}
          </button>
          <button
            onClick={() => handleSort('runsOpenPercent')}
            className={getSortButtonClass('runsOpenPercent')}
          >
            Sort by Runs Open %{getSortIcon('runsOpenPercent')}
          </button>
        </div>

        <div className="bg-gray-200 rounded-lg border border-gray-300 overflow-hidden shadow-lg">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-300 border-b border-gray-400">
                  <th className="px-6 py-4 text-center text-sm font-semibold text-gray-800">
                    Status
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-800">
                    Resort Name
                  </th>
                  <th className="px-6 py-4 text-center text-sm font-semibold text-gray-800">
                    Lifts Open
                  </th>
                  <th className="px-6 py-4 text-center text-sm font-semibold text-gray-800">
                    Runs Open
                  </th>
                  <th className="px-6 py-4 text-center text-sm font-semibold text-white bg-green-600">
                    Green
                  </th>
                  <th className="px-6 py-4 text-center text-sm font-semibold text-white bg-blue-600">
                    Blue
                  </th>
                  <th className="px-6 py-4 text-center text-sm font-semibold text-white bg-gray-800">
                    Black
                  </th>
                  <th className="px-6 py-4 text-center text-sm font-semibold text-white bg-gray-900">
                    Double Black
                  </th>
                  <th className="px-6 py-4 text-center text-sm font-semibold text-gray-800 bg-orange-600">
                    Terrain Park
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-300">
                {getSortedResorts().map((resort) => (
                  <tr
                    key={resort.location}
                    className="hover:bg-gray-100 transition-colors"
                  >
                    <td className="px-6 py-4">
                      <div className="flex justify-center">
                        <div className={`w-4 h-4 rounded-full ${getStatusColor(resort)}`}></div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="font-medium text-gray-900">
                        {resort.location}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="text-gray-900 font-medium">
                        {resort.openLifts}
                      </span>
                      <span className="text-gray-600 text-sm">
                        {' '}/ {resort.totalLifts}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="text-gray-900 font-medium">
                        {resort.openRuns}
                      </span>
                      <span className="text-gray-600 text-sm">
                        {' '}/ {resort.totalRuns}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="text-gray-900 font-medium">
                        {resort.runsByDifficulty.green}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="text-gray-900 font-medium">
                        {resort.runsByDifficulty.blue}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="text-gray-900 font-medium">
                        {resort.runsByDifficulty.black}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="text-gray-900 font-medium">
                        {resort.runsByDifficulty.doubleBlack}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="text-gray-900 font-medium">
                        {resort.runsByDifficulty.terrainPark}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
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

export default DetailsPage

