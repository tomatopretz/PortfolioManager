import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import TimeRangeFilter from './TimeRangeFilter'

function PerformanceChart({ data, timeRange, onTimeRangeChange }) {
  if (!data || data.length === 0) {
    return (
      <div className="flex h-96 items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--surface-1)] p-8 shadow-[var(--shadow-sm)]">
        <p className="font-semibold text-[var(--text-secondary)]">
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
        <div className="rounded border border-[var(--border)] bg-[var(--surface-1)] p-2 shadow-[var(--shadow-lg)]">
          <p className="text-xs font-semibold text-[var(--text-primary)]">
            {payload[0].payload.date}
          </p>
          <p className="text-xs text-[var(--primary)]">
            ${payload[0].value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>
      )
    }
    return null
  }

  const getDateLabel = (dateStr) => {
    const date = new Date(dateStr)
    const dataIndex = data.findIndex((d) => d.date === dateStr)
    const nextDate = dataIndex < data.length - 1 ? new Date(data[dataIndex + 1].date) : null

    if (timeRange === '1d') {
      const hour = date.getHours()
      const minute = date.getMinutes()
      if (minute !== 0) {
        return ''
      }
      return `${hour === 0 ? '12' : hour > 12 ? hour - 12 : hour}${hour >= 12 ? 'p' : 'a'}`
    }

    if (timeRange === '1w') {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    }

    if (timeRange === '1m') {
      const dayOfMonth = date.getDate()
      if (dayOfMonth % 3 !== 1 && dayOfMonth !== 1) {
        return ''
      }
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    }

    if (timeRange === '6m' || timeRange === '1y' || timeRange === 'all') {
      const month = date.getMonth()
      const prevMonth = dataIndex > 0 ? new Date(data[dataIndex - 1].date).getMonth() : null
      if (prevMonth === month) {
        return ''
      }
      return date.toLocaleDateString('en-US', { month: 'short' })
    }

    if (!nextDate || nextDate.getMonth() !== date.getMonth()) {
      return date.toLocaleDateString('en-US', { month: 'short' })
    }
    return ''
  }

  return (
    <div className="h-full rounded-xl border border-[var(--border)] bg-[var(--surface-1)] p-6 shadow-[var(--shadow-sm)]">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-bold text-[var(--text-primary)]">
          Portfolio Performance
        </h3>
        <TimeRangeFilter
          currentRange={timeRange}
          onChange={onTimeRangeChange}
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
            stroke="var(--gridline)"
            vertical={false}
          />
          <XAxis
            dataKey="date"
            interval={0}
            tickFormatter={getDateLabel}
            tick={{ fontSize: 12, fill: 'var(--text-secondary)' }}
            stroke="var(--gridline)"
          />
          <YAxis
            domain={[Math.floor(minValue - range * 0.1), Math.ceil(maxValue + range * 0.1)]}
            tickFormatter={(value) =>
              `$${(value / 1000).toFixed(0)}k`
            }
            tick={{ fontSize: 12, fill: 'var(--text-secondary)' }}
            stroke="var(--gridline)"
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
