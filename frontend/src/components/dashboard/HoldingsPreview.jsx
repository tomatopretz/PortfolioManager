import { Link } from 'react-router-dom'

function HoldingsPreview({ items }) {
  const holdings = items
    .filter((item) => item.assetType !== 'cash')
    .sort((a, b) => b.marketValue - a.marketValue)
    .slice(0, 5)

  if (holdings.length === 0) {
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
          Top Holdings
        </h3>
        <Link
          to="/holdings"
          className="text-sm"
          style={{ color: 'var(--series-1)', textDecoration: 'none' }}
        >
          View all →
        </Link>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr style={{ borderBottom: '1px solid var(--gridline)' }}>
              <th
                className="text-left py-2 px-2"
                style={{ color: 'var(--text-secondary)' }}
              >
                Ticker
              </th>
              <th
                className="text-right py-2 px-2"
                style={{ color: 'var(--text-secondary)' }}
              >
                Qty
              </th>
              <th
                className="text-right py-2 px-2"
                style={{ color: 'var(--text-secondary)' }}
              >
                Price
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
                Gain/Loss
              </th>
            </tr>
          </thead>
          <tbody>
            {holdings.map((item) => {
              const gainLossColor =
                item.gainLoss >= 0
                  ? 'var(--status-good)'
                  : 'var(--status-critical)'

              return (
                <tr
                  key={item.id}
                  style={{ borderBottom: '1px solid var(--gridline)' }}
                >
                  <td className="py-2 px-2" style={{ color: 'var(--text-primary)' }}>
                    {item.ticker}
                  </td>
                  <td className="text-right py-2 px-2" style={{ color: 'var(--text-secondary)' }}>
                    {item.quantity.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                  </td>
                  <td className="text-right py-2 px-2" style={{ color: 'var(--text-secondary)' }}>
                    ${item.currentPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </td>
                  <td className="text-right py-2 px-2" style={{ color: 'var(--text-primary)' }}>
                    ${item.marketValue.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
                  </td>
                  <td className="text-right py-2 px-2" style={{ color: gainLossColor }}>
                    ${item.gainLoss.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ({item.gainLossPercent.toFixed(2)}%)
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default HoldingsPreview
