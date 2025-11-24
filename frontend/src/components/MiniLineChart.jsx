import { useState, useCallback } from 'react'

const MiniLineChart = ({ data, color = '#10b981', maxValue = null, totalCount = null }) => {
  const [hoveredPoint, setHoveredPoint] = useState(null)

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-16 text-slate-500 text-xs">
        No history data
      </div>
    )
  }

  // Find min and max for scaling (relative to data range)
  const values = data.map(d => d.openCount || 0)
  const dataMax = Math.max(...values, 1)
  const dataMin = Math.min(...values, 0)
  
  // Add some padding to the range for better visualization
  const rangePadding = Math.max((dataMax - dataMin) * 0.1, 1)
  const chartMaxValue = dataMax + rangePadding
  const minValue = Math.max(0, dataMin - rangePadding)
  const range = chartMaxValue - minValue || 1

  // SVG dimensions
  const width = 300
  const height = 50
  const padding = 10

  // Calculate points for the line
  const points = data.map((point, index) => {
    const openCount = point.openCount || 0
    const x = padding + (index / (data.length - 1 || 1)) * (width - 2 * padding)
    const y = height - padding - ((openCount - minValue) / range) * (height - 2 * padding)
    return { x, y, value: openCount, date: point.date }
  })

  // Create the line path
  const linePath = points
    .map((point, index) => {
      const command = index === 0 ? 'M' : 'L'
      return `${command} ${point.x} ${point.y}`
    })
    .join(' ')

  // Create the area path (filled under the line)
  const areaPath = `${linePath} L ${width - padding} ${height - padding} L ${padding} ${height - padding} Z`

  const handleMouseEnter = useCallback((point, index) => {
    setHoveredPoint({ ...point, index })
  }, [])

  const handleMouseLeave = useCallback(() => {
    setHoveredPoint(null)
  }, [])

  return (
    <div className="relative flex flex-col items-center w-full">
      <svg width="100%" height={height} className="overflow-visible" viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="xMidYMid meet">
        {/* Tooltip positioned inside SVG using foreignObject */}
        {hoveredPoint && (
          <foreignObject
            x={hoveredPoint.x - 40}
            y={hoveredPoint.y - 70}
            width="80"
            height="50"
            className="overflow-visible pointer-events-none"
          >
            <div className="bg-slate-800 border border-slate-600 rounded px-2 py-1.5 text-xs shadow-lg whitespace-nowrap">
              <div className="text-white font-semibold text-center">{hoveredPoint.date}</div>
              <div className="text-slate-300 text-center">{hoveredPoint.value} open</div>
              {totalCount && (
                <div className="text-slate-400 text-center">
                  {Math.round((hoveredPoint.value / totalCount) * 100)}%
                </div>
              )}
            </div>
          </foreignObject>
        )}
        {/* Grid lines */}
        <line
          x1={padding}
          y1={height - padding}
          x2={width - padding}
          y2={height - padding}
          stroke="rgba(255,255,255,0.1)"
          strokeWidth="1"
        />
        
        {/* Area under the line */}
        <path
          d={areaPath}
          fill={color}
          fillOpacity="0.2"
        />
        
        {/* Line */}
        <path
          d={linePath}
          fill="none"
          stroke={color}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        
        {/* Points */}
        {points.map((point, index) => (
          <g key={index}>
            {/* Larger invisible hit area for better interaction */}
            <circle
              cx={point.x}
              cy={point.y}
              r="8"
              fill="transparent"
              className="cursor-pointer"
              onMouseEnter={() => handleMouseEnter(point, index)}
              onMouseLeave={handleMouseLeave}
            />
            {/* Visible circle */}
            <circle
              cx={point.x}
              cy={point.y}
              r={hoveredPoint && hoveredPoint.index === index ? "5" : "3"}
              fill={color}
              className="pointer-events-none transition-all"
            />
          </g>
        ))}
      </svg>
      
      {/* Date labels */}
      <div className="flex justify-between w-full text-[10px] text-slate-500 mt-1 px-1">
        {data.length > 0 && (
          <>
            <span>{data[0].date}</span>
            <span>{data[data.length - 1].date}</span>
          </>
        )}
      </div>
    </div>
  )
}

export default MiniLineChart

