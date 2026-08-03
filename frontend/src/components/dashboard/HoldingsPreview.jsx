import { Link } from 'react-router-dom'

function HoldingsPreview({ items }) {
  const holdings = items
    .filter((item) => {
      const assetType = String(item.assetType || '').toLowerCase()
      const ticker = String(item.ticker || '').toUpperCase()
      return assetType !== 'cash' && Number(item.marketValue ?? 0) > 0
    })
    .sort((a, b) => b.marketValue - a.marketValue)

  if (holdings.length === 0) {
    return null
  }

  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-1)] p-8 shadow-[var(--shadow-sm)]">
      <div className="mb-6 flex items-center justify-between">
        <h3 className="text-lg font-bold text-[var(--text-primary)]">
          Asset Holdings
        </h3>
        <Link
          to="/holdings"
          className="text-sm font-semibold text-[var(--primary)] transition-colors hover:text-[var(--primary-dark)]"
        >
          View all →
        </Link>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-[var(--border)] bg-[var(--surface-2)]">
              <th className="px-4 py-3 text-left font-semibold text-[var(--text-secondary)]">
                Symbol
              </th>
              <th className="px-4 py-3 text-right font-semibold text-[var(--text-secondary)]">
                Shares
              </th>
              <th className="px-4 py-3 text-right font-semibold text-[var(--text-secondary)]">
                Current Price
              </th>
              <th className="px-4 py-3 text-right font-semibold text-[var(--text-secondary)]">
                Cost Basis
              </th>
              <th className="px-4 py-3 text-right font-semibold text-[var(--text-secondary)]">
                Market Value
              </th>
              <th className="px-4 py-3 text-right font-semibold text-[var(--text-secondary)]">
                P/L
              </th>
            </tr>
          </thead>
          <tbody>
            {holdings.map((item) => {
              const gainLossColor = item.gainLoss >= 0 ? 'text-[var(--status-good)]' : 'text-[var(--status-serious)]'

              return (
                <tr
                  key={item.id}
                  className="border-b border-[var(--border)] transition-colors hover:bg-[var(--surface-2)]"
                >
                  <td className="px-4 py-4 font-semibold text-[var(--text-primary)]">
                    {item.ticker}
                  </td>
                  <td className="px-4 py-4 text-right text-[var(--text-secondary)]">
                    {item.quantity.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                  </td>
                  <td className="px-4 py-4 text-right text-[var(--text-secondary)]">
                    ${item.currentPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </td>
                  <td className="px-4 py-4 text-right text-[var(--text-secondary)]">
                    ${item.costBasis.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </td>
                  <td className="px-4 py-4 text-right font-semibold text-[var(--text-primary)]">
                    ${item.marketValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </td>
                  <td className={`px-4 py-4 text-right font-semibold ${gainLossColor}`}>
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
