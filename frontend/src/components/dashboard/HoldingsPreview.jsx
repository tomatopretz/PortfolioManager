import { Link } from 'react-router-dom'
import { formatCurrency, formatSignedCurrencyOrNA, formatSignedPercentOrNA } from '../../utils/format'

const MAX_PREVIEW_ITEMS = 10

const capitalize = (value) => {
  const str = String(value || '')
  return str.charAt(0).toUpperCase() + str.slice(1)
}

function HoldingsPreview({ items }) {
  const eligible = items.filter((item) => {
    const assetType = String(item.assetType || '').toLowerCase()
    return assetType !== 'cash' && Number(item.marketValue ?? 0) > 0
  })

  const favourited = eligible
    .filter((item) => item.isFavourite)
    .sort((a, b) => String(a.ticker).localeCompare(String(b.ticker)))
  const remainingSlots = Math.max(MAX_PREVIEW_ITEMS - favourited.length, 0)
  const others = eligible
    .filter((item) => !item.isFavourite)
    .sort((a, b) => (b.marketValue ?? 0) - (a.marketValue ?? 0))
    .slice(0, remainingSlots)

  // Favourites always lead, so the star always sorts to the top; the rest are the largest
  // positions by market value.
  const holdings = [...favourited, ...others]
  const remainingCount = eligible.length - holdings.length

  if (holdings.length === 0) {
    return null
  }

  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-1)] p-8 shadow-[var(--shadow-sm)]">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-[var(--text-primary)]">
            Asset Holdings
          </h3>
          <p className="mt-1 text-xs text-[var(--text-secondary)]">
            Your favourites, plus top holdings by market value (max 10)
          </p>
        </div>
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
              <th className="px-4 py-3 text-left font-semibold text-[var(--text-secondary)]">
                Type
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
              const priceAvailable = item.currentPrice != null
              const gainLossColor =
                item.gainLoss == null
                  ? 'text-[var(--text-secondary)]'
                  : item.gainLoss >= 0
                    ? 'text-[var(--status-good)]'
                    : 'text-[var(--status-serious)]'

              return (
                <tr
                  key={item.id}
                  className="border-b border-[var(--border)] transition-colors hover:bg-[var(--surface-2)]"
                >
                  <td className="px-4 py-4 font-semibold text-[var(--text-primary)]">
                    {item.ticker}
                  </td>
                  <td className="px-4 py-4 text-[var(--text-secondary)]">
                    {capitalize(item.assetType)}
                  </td>
                  <td className="px-4 py-4 text-right text-[var(--text-secondary)]">
                    {item.quantity.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                  </td>
                  <td className="px-4 py-4 text-right text-[var(--text-secondary)]">
                    {priceAvailable ? formatCurrency(item.currentPrice) : 'N/A'}
                  </td>
                  <td className="px-4 py-4 text-right text-[var(--text-secondary)]">
                    {formatCurrency(item.costBasis)}
                  </td>
                  <td className="px-4 py-4 text-right font-semibold text-[var(--text-primary)]">
                    {priceAvailable ? formatCurrency(item.marketValue) : 'N/A'}
                  </td>
                  <td className={`px-4 py-4 text-right font-semibold ${gainLossColor}`}>
                    {priceAvailable
                      ? `${formatSignedCurrencyOrNA(item.gainLoss)} (${formatSignedPercentOrNA(item.gainLossPercent)})`
                      : 'N/A'}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {remainingCount > 0 && (
        <p className="mt-4 text-sm text-[var(--text-secondary)]">
          +{remainingCount} more holding{remainingCount !== 1 ? 's' : ''} —{' '}
          <Link to="/holdings" className="font-semibold text-[var(--primary)] hover:text-[var(--primary-dark)]">
            View all
          </Link>
        </p>
      )}
    </div>
  )
}

export default HoldingsPreview
