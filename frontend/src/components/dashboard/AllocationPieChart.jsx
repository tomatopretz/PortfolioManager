import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from 'recharts'
import { useState } from 'react'

const COLORS = [
  'var(--series-1)', // blue
  'var(--series-2)', // orange
  'var(--series-3)', // aqua
  'var(--series-4)', // yellow
  'var(--series-5)', // magenta
  'var(--series-6)', // green
  'var(--series-7)', // violet
  'var(--series-8)', // red
]

function AllocationPieChart({ items }) {
  const [showTable, setShowTable] = useState(false)

  const assetTypes = {}
  items.forEach((item) => {
    if (item.assetType !== 'cash' && item.marketValue > 0) {
      assetTypes[item.assetType] = (assetTypes[item.assetType] || 0) + item.marketValue
    }
  })

  const data = Object.entries(assetTypes).map(([type, value]) => ({
    name: type.charAt(0).toUpperCase() + type.slice(1),
    value: Math.round(value * 100) / 100,
    assetType: type,
  }))

  const total = data.reduce((sum, item) => sum + item.value, 0)

  if (data.length === 0) {
    return (
      <div
        className="rounded-lg border p-6 flex items-center justify-center h-96"
        style={{
          backgroundColor: 'var(--surface-1)',
          borderColor: 'var(--gridline)',
        }}
      >
        <p style={{ color: 'var(--text-muted)' }}>No allocation data available</p>
      </div>
    )
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const entry = payload[0]
      const percent = total > 0 ? ((entry.value / total) * 100).toFixed(1) : 0
      return (
        <div
          className="rounded border p-2 text-sm"
          style={{
            backgroundColor: 'var(--surface-1)',
            borderColor: 'var(--gridline)',
          }}
        >
          <p style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
            {entry.name}
          </p>
          <p style={{ color: 'var(--text-secondary)' }}>
            ${entry.value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
          <p style={{ color: 'var(--text-muted)', fontSize: '12px' }}>
            {percent}% of portfolio
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
      <div className="flex items-center justify-between mb-4">
        <h3
          className="text-lg font-semibold"
          style={{ color: 'var(--text-primary)' }}
        >
          Asset Allocation
        </h3>
        <button
          onClick={() => setShowTable(!showTable)}
          className="text-sm px-3 py-1 rounded"
          style={{
            color: 'var(--series-1)',
            backgroundColor: 'transparent',
            border: '1px solid var(--series-1)',
          }}
        >
          {showTable ? 'Show Chart' : 'Show Table'}
        </button>
      </div>

      {!showTable ? (
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, value }) => {
                const percent = total > 0 ? ((value / total) * 100).toFixed(0) : 0
                return `${name} ${percent}%`
              }}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr style={{ borderBottom: '1px solid var(--gridline)' }}>
                <th
                  className="text-left py-2 px-2"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  Asset Type
                </th>
                <th
                  className="text-right py-2 px-2"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  Value
                </th>
                <th
                  className="text-right py-2 px-2"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  % of Portfolio
                </th>
              </tr>
            </thead>
            <tbody>
              {data.map((entry, index) => {
                const percent = total > 0 ? ((entry.value / total) * 100).toFixed(1) : 0
                return (
                  <tr
                    key={entry.assetType}
                    style={{ borderBottom: '1px solid var(--gridline)' }}
                  >
                    <td className="py-2 px-2">
                      <span className="inline-block w-3 h-3 rounded mr-2"
                        style={{ backgroundColor: COLORS[index % COLORS.length] }} />
                      {entry.name}
                    </td>
                    <td className="text-right py-2 px-2" style={{ color: 'var(--text-primary)' }}>
                      ${entry.value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </td>
                    <td className="text-right py-2 px-2" style={{ color: 'var(--text-secondary)' }}>
                      {percent}%
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default AllocationPieChart
