const RecentlyOpened = ({ data }) => {
  if (!data || (!data.lifts?.length && !data.runs?.length)) {
    return null
  }

  const isToday = (dateString) => {
    if (!dateString) return false
    const today = new Date().toISOString().split('T')[0]
    return dateString.startsWith(today)
  }

  return (
    <div className="bg-white/10 backdrop-blur-sm rounded-lg shadow-xl overflow-hidden border border-white/20 p-6 mb-8">
      <h2 className="text-2xl font-bold text-white mb-6">Recently Opened</h2>
      
      {/* Recently Opened Lifts */}
      {data.lifts && data.lifts.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-slate-300 mb-4 flex items-center gap-2">
            Lifts
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {data.lifts.map((lift, index) => {
              const openedToday = isToday(lift.dateOpened)
              return (
                <div
                  key={index}
                  className="bg-white/5 rounded-lg p-4 border border-white/10 hover:bg-white/10 transition-colors"
                >
                  <div className="text-white font-semibold text-sm mb-2 line-clamp-2" title={lift.name}>
                    {lift.name}
                  </div>
                  <div className="text-slate-400 text-xs mb-1">
                    📍 {lift.location}
                  </div>
                  <div className={`${openedToday ? 'text-green-400' : 'text-slate-400'} text-xs font-medium`}>
                    Opened: {lift.dateOpened}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Recently Opened Runs */}
      {data.runs && data.runs.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-slate-300 mb-4 flex items-center gap-2">
            Runs
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {data.runs.map((run, index) => {
              const openedToday = isToday(run.dateOpened)
              return (
                <div
                  key={index}
                  className="bg-white/5 rounded-lg p-4 border border-white/10 hover:bg-white/10 transition-colors"
                >
                  <div className="text-white font-semibold text-sm mb-2 line-clamp-2" title={run.name}>
                    {run.name}
                  </div>
                  <div className="text-slate-400 text-xs mb-1">
                    📍 {run.location}
                  </div>
                  <div className={`${openedToday ? 'text-blue-400' : 'text-slate-400'} text-xs font-medium`}>
                    Opened: {run.dateOpened}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

export default RecentlyOpened

