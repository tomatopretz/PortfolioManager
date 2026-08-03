import { useMemo, useState } from 'react'
import { usePortfolioContext } from '../context/PortfolioContext'
import LoadingSpinner from '../components/common/LoadingSpinner'
import EmptyState from '../components/common/EmptyState'
import FavouriteStar from '../components/holdings/FavouriteStar'
import HoldingsSummaryCards from '../components/holdings/HoldingsSummaryCards'
import { formatCurrency, formatCurrencyOrNA, formatSignedCurrencyOrNA, formatSignedPercentOrNA } from '../utils/format'

const isCash = (item) => String(item.assetType || '').toLowerCase() === 'cash'
const isZeroQuantity = (item) => Number(item.quantity ?? 0) === 0
const capitalize = (value) => {
  const str = String(value || '')
  return str.charAt(0).toUpperCase() + str.slice(1)
}

const getCostBasisPerShare = (item) => {
  const quantity = Number(item.quantity ?? 0)
  if (quantity === 0) return null
  return (item.costBasis ?? 0) / quantity
}

const formatDate = (value) => {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

const columns = [
  { key: 'ticker', label: 'Ticker' },
  { key: 'assetType', label: 'Type' },
  { key: 'quantity', label: 'Quantity', align: 'right' },
  { key: 'currentPrice', label: 'Current Price', align: 'right' },
  { key: 'costBasis', label: 'Cost Basis', align: 'right' },
  { key: 'costBasisPerShare', label: 'Cost Basis / Share', align: 'right' },
  { key: 'marketValue', label: 'Market Value', align: 'right' },
  { key: 'gainLoss', label: 'Gain/Loss ($)', align: 'right' },
  { key: 'gainLossPercent', label: 'Gain/Loss (%)', align: 'right' },
  { key: 'lastUpdated', label: 'Last Updated', align: 'right' },
]

const compareValues = (a, b, key) => {
  const av = key === 'costBasisPerShare' ? getCostBasisPerShare(a) : a[key]
  const bv = key === 'costBasisPerShare' ? getCostBasisPerShare(b) : b[key]
  if (typeof av === 'string' || typeof bv === 'string') {
    return String(av ?? '').localeCompare(String(bv ?? ''))
  }
  return (av ?? 0) - (bv ?? 0)
}

function HoldingsPage() {
  const { items, itemsLoading, error, getTotalValue, handleToggleFavourite } = usePortfolioContext()
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')
  const [sort, setSort] = useState({ key: 'ticker', direction: 'asc' })

  const assetTypeOptions = useMemo(() => {
    const types = new Set(
      items.map((item) => String(item.assetType || '').toLowerCase()).filter(Boolean)
    )
    return ['all', ...Array.from(types).sort()]
  }, [items])

  if (itemsLoading && items.length === 0) {
    return (
      <div className="flex h-96 items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  if (error && items.length === 0) {
    return (
      <div className="rounded-xl border border-[var(--status-serious)] bg-[var(--surface-1)] p-6 shadow-[var(--shadow-sm)]">
        <p className="font-semibold text-[var(--status-serious)]">
          Error loading portfolio
        </p>
        <p className="mt-1 text-sm text-[var(--text-secondary)]">
          {error}
        </p>
      </div>
    )
  }

  if (items.length === 0) {
    return (
      <div className="space-y-6">
        <h2 className="text-xl font-bold text-[var(--text-primary)]">
          Holdings
        </h2>
        <EmptyState
          title="No Holdings Yet"
          description="Once you add assets to your portfolio, they'll show up here."
        />
      </div>
    )
  }

  const handleSort = (key) => {
    setSort((prev) => {
      if (prev.key === key) {
        return { key, direction: prev.direction === 'asc' ? 'desc' : 'asc' }
      }
      return { key, direction: 'asc' }
    })
  }

  const normalizedSearch = search.trim().toLowerCase()
  const filteredItems = items.filter((item) => {
    const assetType = String(item.assetType || '').toLowerCase()
    const matchesType = typeFilter === 'all' || assetType === typeFilter
    const matchesSearch = normalizedSearch === '' || String(item.ticker || '').toLowerCase().includes(normalizedSearch)
    return matchesType && matchesSearch
  })

  const cashItem = filteredItems.find(isCash)
  const nonCashItems = filteredItems.filter((item) => !isCash(item))

  const direction = sort.direction === 'asc' ? 1 : -1
  const sortedNonCash = [...nonCashItems].sort((a, b) => {
    const aZero = isZeroQuantity(a)
    const bZero = isZeroQuantity(b)
    if (aZero !== bZero) return aZero ? 1 : -1
    return direction * compareValues(a, b, sort.key)
  })

  const rows = cashItem ? [cashItem, ...sortedNonCash] : sortedNonCash
  const holdingsCount = nonCashItems.filter((item) => !isZeroQuantity(item)).length

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-[var(--text-primary)]">
        Holdings
      </h2>

      {error && (
        <div className="rounded-lg border border-[var(--status-serious)] bg-[var(--status-serious)]/10 px-4 py-3 text-sm font-semibold text-[var(--status-serious)]">
          {error}
        </div>
      )}

      <HoldingsSummaryCards items={items} totalValue={getTotalValue()} />

      <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-1)] p-8 shadow-[var(--shadow-sm)]">
        <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by ticker..."
            className="w-full max-w-xs rounded-lg border border-[var(--border)] bg-[var(--surface-1)] px-4 py-2 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:border-[var(--primary)] focus:outline-none"
          />

          <div className="flex w-fit gap-2 rounded-lg bg-[var(--surface-2)] p-1">
            {assetTypeOptions.map((type) => (
              <button
                key={type}
                onClick={() => setTypeFilter(type)}
                className={`rounded-md px-4 py-2 text-sm font-semibold transition-all duration-200 ${
                  typeFilter === type
                    ? 'bg-[var(--primary)] text-white shadow-sm'
                    : 'text-[var(--text-secondary)] hover:bg-[var(--surface-3)] hover:text-[var(--text-primary)]'
                }`}
              >
                {type === 'all' ? 'All' : capitalize(type)}
              </button>
            ))}
          </div>
        </div>

        {rows.length === 0 ? (
          <p className="py-8 text-center text-sm text-[var(--text-secondary)]">
            No holdings match your search/filter.
          </p>
        ) : (
          <div className="max-h-[540px] overflow-y-auto overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="sticky top-0 z-10 border-b border-[var(--border)] bg-[var(--surface-2)]">
                  <th className="px-4 py-3 text-left font-semibold text-[var(--text-secondary)]">
                    Fav
                  </th>
                  {columns.map((col) => (
                    <th
                      key={col.key}
                      onClick={() => handleSort(col.key)}
                      className={`cursor-pointer select-none px-4 py-3 font-semibold text-[var(--text-secondary)] hover:text-[var(--text-primary)] ${
                        col.align === 'right' ? 'text-right' : 'text-left'
                      }`}
                    >
                      {col.label}
                      {sort.key === col.key && (sort.direction === 'asc' ? ' ▲' : ' ▼')}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((item) => {
                  const cash = isCash(item)
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
                      <td className="px-4 py-4">
                        <FavouriteStar
                          active={!!item.isFavourite}
                          disabled={cash || isZeroQuantity(item)}
                          onToggle={() => handleToggleFavourite(item)}
                        />
                      </td>
                      <td className="px-4 py-4 font-semibold text-[var(--text-primary)]">
                        {item.ticker}
                      </td>
                      <td className="px-4 py-4 text-[var(--text-secondary)]">
                        {capitalize(item.assetType)}
                      </td>
                      <td className="px-4 py-4 text-right text-[var(--text-secondary)]">
                        {Number(item.quantity ?? 0).toLocaleString('en-US', { maximumFractionDigits: 2 })}
                      </td>
                      <td className="px-4 py-4 text-right text-[var(--text-secondary)]">
                        {priceAvailable ? formatCurrency(item.currentPrice) : 'N/A'}
                      </td>
                      <td className="px-4 py-4 text-right text-[var(--text-secondary)]">
                        {formatCurrency(item.costBasis)}
                      </td>
                      <td className="px-4 py-4 text-right text-[var(--text-secondary)]">
                        {formatCurrencyOrNA(getCostBasisPerShare(item))}
                      </td>
                      <td className="px-4 py-4 text-right font-semibold text-[var(--text-primary)]">
                        {priceAvailable ? formatCurrency(item.marketValue) : 'N/A'}
                      </td>
                      <td className={`px-4 py-4 text-right font-semibold ${gainLossColor}`}>
                        {formatSignedCurrencyOrNA(item.gainLoss)}
                      </td>
                      <td className={`px-4 py-4 text-right font-semibold ${gainLossColor}`}>
                        {formatSignedPercentOrNA(item.gainLossPercent)}
                      </td>
                      <td className="px-4 py-4 text-right text-[var(--text-secondary)]">
                        {formatDate(item.lastUpdated)}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}

        <p className="mt-4 text-right text-sm text-[var(--text-secondary)]">
          {holdingsCount} holding{holdingsCount !== 1 ? 's' : ''}
        </p>
      </div>
    </div>
  )
}

export default HoldingsPage
