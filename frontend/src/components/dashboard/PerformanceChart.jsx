import { useMemo } from 'react'
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import Card from '../common/Card'
import TimeRangeFilter from './TimeRangeFilter'
import { PRIMARY_SERIES_COLOR } from '../../constants/portfolio'
import { formatCompactCurrency, formatCurrency } from '../../utils/format'

const INTRADAY_RANGE = '1d'
const MONTHLY_TICK_RANGES = new Set(['6m', '1y', 'all'])
const GRADIENT_ID = 'performance-area-gradient'

const formatHourTick = (timestamp) => {
  const hour = new Date(timestamp).getHours()
  const displayHour = hour % 12 === 0 ? 12 : hour % 12
  return `${displayHour}${hour >= 12 ? 'pm' : 'am'}`
}

const INTRADAY_TICK_HOURS = 2

/** One tick every other whole hour covered by the intraday series. */
const buildHourlyTicks = (points) => {
  if (points.length === 0) return []
  const timestamps = points.map((point) => point.timestamp)
  const min = Math.min(...timestamps)
  const max = Math.max(...timestamps)

  const cursor = new Date(min)
  cursor.setMinutes(0, 0, 0)
  if (cursor.getTime() < min) cursor.setHours(cursor.getHours() + 1)

  const ticks = []
  while (cursor.getTime() <= max) {
    ticks.push(cursor.getTime())
    cursor.setHours(cursor.getHours() + INTRADAY_TICK_HOURS)
  }
  return ticks
}

/**
 * Precomputes the X-axis label for every point, keyed by date. Doing this once (rather than
 * inside `tickFormatter`) avoids an O(n) `findIndex` per tick, and keeps the thinning rules -
 * every 3rd day for 1M, first-of-month for the longer ranges - in one readable place.
 */
const buildDateLabels = (data, timeRange) => {
  const shortDate = (date) => date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  const labels = new Map()

  data.forEach((point, index) => {
    const date = new Date(point.date)

    if (timeRange === '1w') {
      labels.set(point.date, shortDate(date))
      return
    }

    if (timeRange === '1m') {
      // Roughly every third day, so labels don't collide.
      labels.set(point.date, date.getDate() % 3 === 1 ? shortDate(date) : '')
      return
    }

    if (MONTHLY_TICK_RANGES.has(timeRange)) {
      const previousMonth = index > 0 ? new Date(data[index - 1].date).getMonth() : null
      const isNewMonth = previousMonth !== date.getMonth()
      labels.set(point.date, isNewMonth ? date.toLocaleDateString('en-US', { month: 'short' }) : '')
      return
    }

    labels.set(point.date, shortDate(date))
  })

  return labels
}

function PerformanceTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded border border-[var(--border)] bg-[var(--surface-1)] p-2 shadow-[var(--shadow-lg)]">
      <p className="text-sm font-semibold text-[var(--text-primary)]">{payload[0].payload.date}</p>
      <p className="text-sm text-[var(--primary)]">{formatCurrency(payload[0].value)}</p>
    </div>
  )
}

const AXIS_TICK = { fontSize: 14, fill: 'var(--text-secondary)' }

function PerformanceChart({ data, timeRange, onTimeRangeChange }) {
  const isIntraday = timeRange === INTRADAY_RANGE
  const points = data ?? []

  const chartData = useMemo(
    () =>
      isIntraday
        ? points.map((point) => ({ ...point, timestamp: new Date(point.date).getTime() }))
        : points,
    [points, isIntraday]
  )

  const hourlyTicks = useMemo(
    () => (isIntraday ? buildHourlyTicks(chartData) : []),
    [chartData, isIntraday]
  )

  const dateLabels = useMemo(
    () => (isIntraday ? new Map() : buildDateLabels(points, timeRange)),
    [points, timeRange, isIntraday]
  )

  const yDomain = useMemo(() => {
    if (points.length === 0) return [0, 0]
    const values = points.map((point) => point.totalValue)
    const min = Math.min(...values)
    const max = Math.max(...values)
    const padding = (max - min) * 0.1
    return [Math.floor(min - padding), Math.ceil(max + padding)]
  }, [points])

  if (points.length === 0) {
    return (
      <Card padding="p-8" className="flex h-96 items-center justify-center">
        <p className="font-semibold text-[var(--text-secondary)]">No performance data available</p>
      </Card>
    )
  }

  return (
    <Card className="h-full">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-bold text-[var(--text-primary)]">Portfolio Performance</h3>
        <TimeRangeFilter timeRange={timeRange} onTimeRangeChange={onTimeRangeChange} />
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id={GRADIENT_ID} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={PRIMARY_SERIES_COLOR} stopOpacity={0.3} />
              <stop offset="95%" stopColor={PRIMARY_SERIES_COLOR} stopOpacity={0} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="var(--gridline)" vertical={false} />

          {isIntraday ? (
            <XAxis
              dataKey="timestamp"
              type="number"
              domain={['dataMin', 'dataMax']}
              ticks={hourlyTicks}
              tickFormatter={formatHourTick}
              tick={AXIS_TICK}
              stroke="var(--gridline)"
            />
          ) : (
            <XAxis
              dataKey="date"
              interval={0}
              tickFormatter={(date) => dateLabels.get(date) ?? ''}
              tick={AXIS_TICK}
              stroke="var(--gridline)"
            />
          )}

          <YAxis
            domain={yDomain}
            tickFormatter={formatCompactCurrency}
            tick={AXIS_TICK}
            stroke="var(--gridline)"
          />

          <Tooltip content={<PerformanceTooltip />} />

          <Area
            type="monotone"
            dataKey="totalValue"
            stroke={PRIMARY_SERIES_COLOR}
            strokeWidth={2}
            fillOpacity={1}
            fill={`url(#${GRADIENT_ID})`}
            dot={false}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </Card>
  )
}

export default PerformanceChart
