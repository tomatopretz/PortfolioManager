import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import { useState } from 'react'

const COLORS = [
  '#3b82f6',
  '#f97316',
  '#10b981',
  '#eab308',
  '#ec4899',
  '#22c55e',
  '#8b5cf6',
  '#ef4444',
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
      <div className="flex h-96 items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--surface-1)] p-8 shadow-[var(--shadow-sm)]">
        <p className="font-semibold text-[var(--text-secondary)]">
          No allocation data available
        </p>
      </div>
    )
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const entry = payload[0]
      const percent = total > 0 ? ((entry.value / total) * 100).toFixed(1) : 0
      return (
        <div className="rounded border border-[var(--border)] bg-[var(--surface-1)] p-2 text-sm shadow-[var(--shadow-lg)]">
          <p className="font-semibold text-[var(--text-primary)]">
            {entry.name}
          </p>
          <p className="text-[var(--text-secondary)]">
            ${entry.value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
          <p className="text-xs text-[var(--text-muted)]">
            {percent}% of portfolio
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="h-full rounded-xl border border-[var(--border)] bg-[var(--surface-1)] p-8 shadow-[var(--shadow-sm)]">
      <div className="mb-6 flex items-center justify-between">
        <h3 className="text-lg font-bold text-[var(--text-primary)]">
          Asset Allocation
        </h3>
        <button
          onClick={() => setShowTable(!showTable)}
          className="rounded-lg border border-[var(--primary)] bg-[var(--primary)]/10 px-4 py-2 text-xs font-semibold text-[var(--primary)] transition-all duration-200 hover:bg-[var(--primary)]/20 hover:shadow-md"
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
              fill="#3b82f6"
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
              <tr className="border-b border-[var(--border)] bg-[var(--surface-2)]">
                <th className="px-4 py-3 text-left font-semibold text-[var(--text-secondary)]">
                  Asset Type
                </th>
                <th className="px-4 py-3 text-right font-semibold text-[var(--text-secondary)]">
                  Value
                </th>
                <th className="px-4 py-3 text-right font-semibold text-[var(--text-secondary)]">
                  % of Portfolio
                </th>
              </tr>
            </thead>
            <tbody>
              {data.map((entry, index) => {
                const percent = total > 0 ? ((entry.value / total) * 100).toFixed(1) : 0
                return (
                  <tr key={entry.assetType} className="border-b border-[var(--border)] transition-colors hover:bg-[var(--surface-2)]">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <span
                          className="inline-block h-3 w-3 rounded-full"
                          style={{ backgroundColor: COLORS[index % COLORS.length] }}
                        />
                        <span className="text-[var(--text-primary)]">{entry.name}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right font-semibold text-[var(--text-primary)]">
                      ${entry.value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </td>
                    <td className="px-4 py-3 text-right text-[var(--text-secondary)]">
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
