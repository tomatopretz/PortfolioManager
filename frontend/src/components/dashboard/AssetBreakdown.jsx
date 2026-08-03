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
    const assetType = String(item.assetType || '').toLowerCase()
    const ticker = String(item.ticker || '').toUpperCase()
    if (assetType !== 'cash' && item.marketValue > 0) {
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
    <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-1)] p-8 shadow-[var(--shadow-sm)]">
      <h3 className="mb-6 text-lg font-bold text-[var(--text-primary)]">
        Asset Breakdown by Type
      </h3>

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
            {data.map((row, index) => (
              <tr
                key={row.type}
                className="border-b border-[var(--border)] transition-colors hover:bg-[var(--surface-2)]"
              >
                <td className="px-4 py-4">
                  <div className="flex items-center gap-3">
                    <div
                      className="h-3 w-3 rounded-full"
                      style={{
                        backgroundColor: COLORS[index % COLORS.length],
                      }}
                    />
                    <span className="font-medium text-[var(--text-primary)]">
                      {row.type}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-4 text-right font-semibold text-[var(--text-primary)]">
                  ${row.value.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </td>
                <td className="px-4 py-4 text-right text-[var(--text-secondary)]">
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
