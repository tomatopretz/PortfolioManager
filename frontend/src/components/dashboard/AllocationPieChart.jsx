import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import { useState } from 'react'

const COLORS = [
  '#3b82f6', // blue
  '#f97316', // orange
  '#10b981', // green
  '#eab308', // yellow
  '#ec4899', // magenta
  '#22c55e', // green
  '#8b5cf6', // violet
  '#ef4444', // red
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
      <div className="bg-white rounded-xl border border-gray-200 p-8 flex items-center justify-center h-96 shadow-sm">
        <p className="font-semibold text-gray-600">
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
        <div className="bg-white rounded border border-gray-200 p-2 text-sm shadow-lg">
          <p className="font-semibold text-gray-900">
            {entry.name}
          </p>
          <p className="text-gray-600">
            ${entry.value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
          <p className="text-gray-500 text-xs">
            {percent}% of portfolio
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-8 h-full shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-bold text-gray-900">
          Asset Allocation
        </h3>
        <button
          onClick={() => setShowTable(!showTable)}
          className="text-xs px-4 py-2 rounded-lg font-semibold text-blue-600 bg-blue-50 border border-blue-300 hover:bg-blue-100 transition-all duration-200 hover:shadow-md"
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
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="text-left py-3 px-4 font-semibold text-gray-700">
                  Asset Type
                </th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">
                  Value
                </th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">
                  % of Portfolio
                </th>
              </tr>
            </thead>
            <tbody>
              {data.map((entry, index) => {
                const percent = total > 0 ? ((entry.value / total) * 100).toFixed(1) : 0
                return (
                  <tr key={entry.assetType} className="border-b border-gray-200 hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-3">
                        <span
                          className="inline-block w-3 h-3 rounded-full"
                          style={{ backgroundColor: COLORS[index % COLORS.length] }}
                        />
                        <span className="text-gray-900">{entry.name}</span>
                      </div>
                    </td>
                    <td className="text-right py-3 px-4 font-semibold text-gray-900">
                      ${entry.value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </td>
                    <td className="text-right py-3 px-4 text-gray-600">
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
