import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

function PerformanceChart({ data, timeRange }) {
  if (!data || data.length === 0) {
    return (
      <div
        className="rounded-lg border p-6 flex items-center justify-center h-96"
        style={{
          backgroundColor: 'var(--surface-1)',
          borderColor: 'var(--gridline)',
        }}
      >
        <p style={{ color: 'var(--text-muted)' }}>No performance data available</p>
      </div>
    )
  }

  const minValue = Math.min(...data.map((d) => d.totalValue))
  const maxValue = Math.max(...data.map((d) => d.totalValue))
  const range = maxValue - minValue

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div
          className="rounded border p-2"
          style={{
            backgroundColor: 'var(--surface-1)',
            borderColor: 'var(--gridline)',
          }}
        >
          <p style={{ color: 'var(--text-primary)', fontWeight: 600, fontSize: '12px' }}>
            {payload[0].payload.date}
          </p>
          <p style={{ color: 'var(--series-1)', fontSize: '12px' }}>
            ${payload[0].value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div
      className="rounded-lg border p-6"
      style={{
        backgroundColor: 'var(--surface-1)',
        borderColor: 'var(--gridline)',
      }}
    >
      <h3
        className="text-lg font-semibold mb-4"
        style={{ color: 'var(--text-primary)' }}
      >
        Portfolio Performance ({timeRange.toUpperCase()})
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="var(--series-1)" stopOpacity={0.3} />
              <stop offset="95%" stopColor="var(--series-1)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="var(--gridline)"
            vertical={false}
          />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12, fill: 'var(--text-muted)' }}
            stroke="var(--gridline)"
            style={{ color: 'var(--text-muted)' }}
          />
          <YAxis
            domain={[Math.floor(minValue - range * 0.1), Math.ceil(maxValue + range * 0.1)]}
            tickFormatter={(value) =>
              `$${(value / 1000).toFixed(0)}k`
            }
            tick={{ fontSize: 12, fill: 'var(--text-muted)' }}
            stroke="var(--gridline)"
            style={{ color: 'var(--text-muted)' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="totalValue"
            stroke="var(--series-1)"
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
