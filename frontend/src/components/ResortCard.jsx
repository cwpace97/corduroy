import { useState } from 'react'
import MiniLineChart from './MiniLineChart'

const DifficultyBadge = ({ difficulty }) => {
  const colors = {
    'green': 'bg-green-500',
    'blue1': 'bg-blue-500',
    'blue2': 'bg-blue-500',
    'black1': 'bg-black',
    'black2': 'bg-black',
    'Unknown': 'bg-gray-500'
  }

  const labels = {
    'green': '●',
    'blue1': '■',
    'blue2': '▣▣',
    'black1': '◆',
    'black2': '◆◆',
    'Unknown': '?'
  }

  return (
    <span className={`${colors[difficulty] || colors.Unknown} text-white px-2 py-0.5 rounded text-xs font-bold`}>
      {labels[difficulty] || '?'}
    </span>
  )
}

const StatusBadge = ({ status }) => {
  const isOpen = status === 'Open'
  return (
    <span className={`${isOpen ? 'bg-green-500' : 'bg-red-500'} text-white px-2 py-1 rounded text-xs font-semibold`}>
      {status}
    </span>
  )
}

const ResortCard = ({ resort }) => {
  const [showDetails, setShowDetails] = useState(false)

  const handleToggleDetails = () => {
    setShowDetails(!showDetails)
  }

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      handleToggleDetails()
    }
  }

  const liftOpenPercentage = resort.totalLifts > 0 
    ? Math.round((resort.openLifts / resort.totalLifts) * 100) 
    : 0

  const runOpenPercentage = resort.totalRuns > 0 
    ? Math.round((resort.openRuns / resort.totalRuns) * 100) 
    : 0

  // Sort lifts: open first (alphabetically), then closed (alphabetically)
  const sortedLifts = [...resort.lifts].sort((a, b) => {
    if (a.liftStatus === 'Open' && b.liftStatus !== 'Open') return -1
    if (a.liftStatus !== 'Open' && b.liftStatus === 'Open') return 1
    return a.liftName.localeCompare(b.liftName)
  })

  // Sort runs: open first (alphabetically), then closed (alphabetically)
  const sortedRuns = [...resort.runs].sort((a, b) => {
    if (a.runStatus === 'Open' && b.runStatus !== 'Open') return -1
    if (a.runStatus !== 'Open' && b.runStatus === 'Open') return 1
    return a.runName.localeCompare(b.runName)
  })

  return (
    <div className="bg-white/10 backdrop-blur-sm rounded-lg shadow-xl overflow-hidden border border-white/20">
      {/* Summary Section - Always Visible */}
      <div 
        className="p-6 cursor-pointer hover:bg-white/5 transition-colors"
        onClick={handleToggleDetails}
        onKeyDown={handleKeyDown}
        role="button"
        tabIndex={0}
        aria-expanded={showDetails}
        aria-label={`Toggle details for ${resort.location}`}
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-3xl font-bold text-white">{resort.location}</h2>
          <div className="text-sm text-slate-300">
            Last updated: {resort.lastUpdated}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left side - Lifts and Runs Status with History */}
          <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Lifts Combined */}
            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
              <div className="text-slate-400 text-sm mb-3 font-semibold">Lifts Open</div>
              <div className="flex items-end justify-between mb-3">
                <div className="text-4xl font-bold text-white">
                  {resort.openLifts}<span className="text-2xl text-slate-400">/{resort.totalLifts}</span>
                </div>
                <div className="text-lg text-slate-300">{liftOpenPercentage}%</div>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2 mb-4">
                <div 
                  className="bg-green-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${liftOpenPercentage}%` }}
                />
              </div>
              
              {/* 7 Day History */}
              <div className="border-t border-white/10 pt-3 mt-3">
                <div className="text-slate-400 text-xs mb-2">7 Day History</div>
                <MiniLineChart 
                  data={resort.liftsHistory} 
                  color="#10b981"
                  maxValue={resort.totalLifts}
                  totalCount={resort.totalLifts}
                />
              </div>
            </div>

            {/* Runs Combined */}
            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
              <div className="text-slate-400 text-sm mb-3 font-semibold">Runs Open</div>
              <div className="flex items-end justify-between mb-3">
                <div className="text-4xl font-bold text-white">
                  {resort.openRuns}<span className="text-2xl text-slate-400">/{resort.totalRuns}</span>
                </div>
                <div className="text-lg text-slate-300">{runOpenPercentage}%</div>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2 mb-4">
                <div 
                  className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${runOpenPercentage}%` }}
                />
              </div>
              
              {/* 7 Day History */}
              <div className="border-t border-white/10 pt-3 mt-3">
                <div className="text-slate-400 text-xs mb-2">7 Day History</div>
                <MiniLineChart 
                  data={resort.runsHistory} 
                  color="#3b82f6"
                  maxValue={resort.totalRuns}
                  totalCount={resort.totalRuns}
                />
              </div>
            </div>
          </div>

          {/* Right side - Recently Opened */}
          <div className="space-y-4">
            {/* Recently Opened Lifts */}
            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
              <div className="text-slate-400 text-sm mb-3 font-semibold">Recently Opened Lifts</div>
              <div className="space-y-2">
                {resort.recentlyOpenedLifts && resort.recentlyOpenedLifts.length > 0 ? (
                  resort.recentlyOpenedLifts.map((lift, index) => (
                    <div 
                      key={index}
                      className="bg-white/5 rounded p-2 border border-white/10"
                    >
                      <div className="text-white text-sm font-medium">{lift.name}</div>
                      <div className="text-slate-400 text-xs mt-1">{lift.dateOpened}</div>
                    </div>
                  ))
                ) : (
                  <div className="text-slate-500 text-xs">No recent data</div>
                )}
              </div>
            </div>

            {/* Recently Opened Runs */}
            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
              <div className="text-slate-400 text-sm mb-3 font-semibold">Recently Opened Runs</div>
              <div className="space-y-2">
                {resort.recentlyOpenedRuns && resort.recentlyOpenedRuns.length > 0 ? (
                  resort.recentlyOpenedRuns.map((run, index) => (
                    <div 
                      key={index}
                      className="bg-white/5 rounded p-2 border border-white/10"
                    >
                      <div className="text-white text-sm font-medium">{run.name}</div>
                      <div className="text-slate-400 text-xs mt-1">{run.dateOpened}</div>
                    </div>
                  ))
                ) : (
                  <div className="text-slate-500 text-xs">No recent data</div>
                )}
              </div>
            </div>

            {/* View Details Button */}
            <div className="bg-white/5 rounded-lg p-4 border border-white/10 flex items-center justify-center">
              <button 
                className="text-sky-400 hover:text-sky-300 font-semibold text-lg transition-colors"
                aria-label={showDetails ? 'Hide details' : 'Show details'}
              >
                {showDetails ? '▲ Hide Details' : '▼ View Details'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Details Section - Expandable */}
      {showDetails && (
        <div className="border-t border-white/20 bg-white/5 p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Lifts Details */}
            <div>
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                🚡 Lifts ({resort.lifts.length})
              </h3>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {sortedLifts.map((lift, index) => (
                  <div 
                    key={index} 
                    className="bg-white/5 rounded p-3 flex items-center justify-between border border-white/10"
                  >
                    <div className="flex items-center gap-2 flex-wrap flex-1">
                      <div className="text-white font-medium">{lift.liftName}</div>
                      {lift.liftType && (
                        <div className="inline-block bg-slate-600 border border-slate-500 rounded px-2 py-0.5">
                          <span className="text-slate-300 text-xs">{lift.liftType}</span>
                        </div>
                      )}
                      {lift.liftStatus === 'Open' && lift.dateOpened && (
                        <div className="inline-block bg-slate-700 border border-slate-600 rounded px-2 py-0.5">
                          <span className="text-slate-300 text-xs">Opened: {lift.dateOpened}</span>
                        </div>
                      )}
                    </div>
                    <StatusBadge status={lift.liftStatus} />
                  </div>
                ))}
              </div>
            </div>

            {/* Runs Details */}
            <div>
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                ⛷️ Runs ({resort.runs.length})
              </h3>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {sortedRuns.map((run, index) => (
                  <div 
                    key={index} 
                    className="bg-white/5 rounded p-3 flex items-center justify-between border border-white/10"
                  >
                    <div className="flex items-center gap-2 flex-1">
                      <DifficultyBadge difficulty={run.runDifficulty} />
                      <div className="flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <div className="text-white font-medium">{run.runName}</div>
                          {run.runStatus === 'Open' && run.dateOpened && (
                            <div className="inline-block bg-slate-700 border border-slate-600 rounded px-2 py-0.5">
                              <span className="text-slate-300 text-xs">Opened: {run.dateOpened}</span>
                            </div>
                          )}
                        </div>
                        {run.runGroomed && (
                          <div className="text-slate-400 text-xs">✓ Groomed</div>
                        )}
                      </div>
                    </div>
                    <StatusBadge status={run.runStatus} />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ResortCard

