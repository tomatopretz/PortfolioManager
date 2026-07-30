const COLORS = [
  '#3b82f6',
  '#f97316',
  '#10b981',
  '#eab308',
  '#ec4899',
]

function AssetBreakdown({ items }) {
  const assetBreakdown = {}
  let totalValue = 0

  items.forEach((item) => {
    if (item.assetType !== 'cash') {
      assetBreakdown[item.assetType] = (assetBreakdown[item.assetType] || 0) + item.marketValue
      totalValue += item.marketValue
    }
  })

  const data = Object.entries(assetBreakdown)
    .map(([type, value]) => ({
      type: type.charAt(0).toUpperCase() + type.slice(1),
      value: Math.round(value * 100) / 100,
      percent: totalValue > 0 ? ((value / totalValue) * 100).toFixed(1) : 0,
    }))
    .sort((a, b) => b.value - a.value)

  if (data.length === 0) return null

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-8 shadow-sm">
      <h3 className="text-lg font-bold text-gray-900 mb-6">
        Asset Breakdown by Type
      </h3>

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
            {data.map((row, index) => (
              <tr
                key={row.type}
                className="border-b border-gray-200 hover:bg-gray-50 transition-colors"
              >
                <td className="py-4 px-4">
                  <div className="flex items-center gap-3">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{
                        backgroundColor: COLORS[index % COLORS.length],
                      }}
                    />
                    <span className="text-gray-900 font-medium">
                      {row.type}
                    </span>
                  </div>
                </td>
                <td className="text-right py-4 px-4 font-semibold text-gray-900">
                  ${row.value.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </td>
                <td className="text-right py-4 px-4 text-gray-700">
                  {row.percent}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default AssetBreakdown
