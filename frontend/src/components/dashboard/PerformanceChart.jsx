import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import TimeRangeFilter from './TimeRangeFilter'

function PerformanceChart({ data, timeRange, onTimeRangeChange }) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-8 flex items-center justify-center h-96 shadow-sm">
        <p className="font-semibold text-gray-600">
          No performance data available
        </p>
      </div>
    )
  }

  const minValue = Math.min(...data.map((d) => d.totalValue))
  const maxValue = Math.max(...data.map((d) => d.totalValue))
  const range = maxValue - minValue

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white rounded border border-gray-200 p-2 shadow-lg">
          <p className="font-semibold text-gray-900 text-xs">
            {payload[0].payload.date}
          </p>
          <p className="text-blue-600 text-xs">
            ${payload[0].value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>
      )
    }
    return null
  }

  const getDateLabel = (dateStr) => {
    const date = new Date(dateStr)
    const dataIndex = data.findIndex(d => d.date === dateStr)
    const currentDate = new Date(dateStr)
    const nextDate = dataIndex < data.length - 1 ? new Date(data[dataIndex + 1].date) : null

    if (timeRange === '1d') {
      const hour = date.getHours()
      return `${hour === 0 ? '12' : hour > 12 ? hour - 12 : hour}${hour >= 12 ? 'p' : 'a'}`
    }

    if (timeRange === '1w') {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    }

    if (timeRange === '1m') {
      if (!nextDate || nextDate.getMonth() !== currentDate.getMonth()) {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      }
      return ''
    }

    if (!nextDate || nextDate.getMonth() !== currentDate.getMonth()) {
      return date.toLocaleDateString('en-US', { month: 'short' })
    }
    return ''
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 h-full shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900">
          Portfolio Performance
        </h3>
        <TimeRangeFilter
          timeRange={timeRange}
          onTimeRangeChange={onTimeRangeChange}
        />
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#e5e7eb"
            vertical={false}
          />
          <XAxis
            dataKey="date"
            tickFormatter={getDateLabel}
            tick={{ fontSize: 12, fill: '#999999' }}
            stroke="#e5e7eb"
          />
          <YAxis
            domain={[Math.floor(minValue - range * 0.1), Math.ceil(maxValue + range * 0.1)]}
            tickFormatter={(value) =>
              `$${(value / 1000).toFixed(0)}k`
            }
            tick={{ fontSize: 12, fill: '#999999' }}
            stroke="#e5e7eb"
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="totalValue"
            stroke="#3b82f6"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorValue)"
            dot={false}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

export default PerformanceChart
