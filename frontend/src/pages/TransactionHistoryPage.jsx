import { useEffect, useMemo, useState } from 'react'
import { usePortfolioContext } from '../context/PortfolioContext'
import { getTransactions } from '../services'
import LoadingSpinner from '../components/common/LoadingSpinner'
import EmptyState from '../components/common/EmptyState'
import TransactionSummaryCards from '../components/transactions/TransactionSummaryCards'
import { formatCurrency } from '../utils/format'

const capitalize = (value) => {
  const str = String(value || '')
  return str.charAt(0).toUpperCase() + str.slice(1)
}

const formatDate = (value) => {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

const columns = [
  { key: 'date', label: 'Date' },
  { key: 'ticker', label: 'Ticker' },
  { key: 'assetType', label: 'Type' },
  { key: 'action', label: 'Action' },
  { key: 'quantity', label: 'Quantity', align: 'right' },
  { key: 'price', label: 'Price', align: 'right' },
  { key: 'total', label: 'Total', align: 'right' },
  { key: 'useCash', label: 'Cash Used', align: 'right' },
]

const actionLabels = {
  buy: 'Buy',
  sell: 'Sell',
  deposit: 'Deposit',
  withdrawal: 'Withdrawal',
}

// A buy/sell of a non-cash asset that used cash records a second, auto-generated Transaction
// row against the CASH item (opposite type, same date, amount = quantity * price) so the CASH
// balance stays in sync. That row isn't a distinct user action - it's collapsed into the asset
// row it belongs to so buy/sell counts reflect actual trades. Cash rows that don't pair up with
// an asset trade are real deposits/withdrawals and are kept, just labeled accordingly.
const collapseCashLegs = (enrichedTransactions) => {
  const assetTxs = enrichedTransactions.filter((t) => t.assetType !== 'cash')
  const cashTxs = enrichedTransactions.filter((t) => t.assetType === 'cash')
  const mergedCashIds = new Set()

  assetTxs.forEach((t) => {
    if (!t.useCash) return
    const expectedCashType = t.type === 'buy' ? 'sell' : 'buy'
    const match = cashTxs.find((c) => (
      !mergedCashIds.has(c.id) &&
      c.type === expectedCashType &&
      new Date(c.date).getTime() === new Date(t.date).getTime() &&
      Math.abs(c.quantity - t.total) < 0.01
    ))
    if (match) mergedCashIds.add(match.id)
  })

  return enrichedTransactions
    .filter((t) => !mergedCashIds.has(t.id))
    .map((t) => {
      if (t.assetType === 'cash') {
        return { ...t, action: t.type === 'buy' ? 'deposit' : 'withdrawal' }
      }
      return { ...t, action: t.type }
    })
}

const compareValues = (a, b, key) => {
  if (key === 'date') {
    return new Date(a.date).getTime() - new Date(b.date).getTime()
  }
  const av = a[key]
  const bv = b[key]
  if (typeof av === 'boolean' || typeof bv === 'boolean') {
    return Number(av) - Number(bv)
  }
  if (typeof av === 'string' || typeof bv === 'string') {
    return String(av ?? '').localeCompare(String(bv ?? ''))
  }
  return (av ?? 0) - (bv ?? 0)
}

function TransactionHistoryPage() {
  const { items } = usePortfolioContext()
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')
  const [sort, setSort] = useState({ key: 'date', direction: 'desc' })

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    getTransactions()
      .then((data) => {
        if (!cancelled) setTransactions(data || [])
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const itemById = useMemo(() => new Map(items.map((item) => [item.id, item])), [items])

  const enrichedTransactions = useMemo(() => {
    const withTotals = transactions.map((t) => {
      const relatedItem = itemById.get(t.portfolioItemId)
      return {
        ...t,
        ticker: relatedItem?.ticker ?? 'Unknown',
        assetType: relatedItem ? String(relatedItem.assetType || '').toLowerCase() : 'unknown',
        total: Number(t.quantity ?? 0) * Number(t.price ?? 0),
      }
    })
    return collapseCashLegs(withTotals)
  }, [transactions, itemById])

  if (loading && transactions.length === 0) {
    return (
      <div className="flex h-96 items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  if (error && transactions.length === 0) {
    return (
      <div className="rounded-xl border border-[var(--status-serious)] bg-[var(--surface-1)] p-6 shadow-[var(--shadow-sm)]">
        <p className="font-semibold text-[var(--status-serious)]">
          Error loading transactions
        </p>
        <p className="mt-1 text-sm text-[var(--text-secondary)]">
          {error}
        </p>
      </div>
    )
  }

  if (enrichedTransactions.length === 0) {
    return (
      <div className="space-y-6">
        <h2 className="text-xl font-bold text-[var(--text-primary)]">
          Transaction History
        </h2>
        <EmptyState
          title="No Transactions Yet"
          description="Once you buy or sell an asset, it will show up here."
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
  const filteredTransactions = enrichedTransactions.filter((t) => {
    const matchesType = typeFilter === 'all' || t.action === typeFilter
    const matchesSearch = normalizedSearch === '' || t.ticker.toLowerCase().includes(normalizedSearch)
    return matchesType && matchesSearch
  })

  const direction = sort.direction === 'asc' ? 1 : -1
  const rows = [...filteredTransactions].sort((a, b) => direction * compareValues(a, b, sort.key))

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-[var(--text-primary)]">
        Transaction History
      </h2>

      <TransactionSummaryCards transactions={enrichedTransactions} />

      <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-1)] p-8 shadow-[var(--shadow-sm)]">
        <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by ticker..."
            className="w-full max-w-xs rounded-lg border border-[var(--border)] bg-[var(--surface-1)] px-4 py-2 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:border-[var(--primary)] focus:outline-none"
          />

          <div className="flex w-fit flex-wrap gap-2 rounded-lg bg-[var(--surface-2)] p-1">
            {['all', 'buy', 'sell', 'deposit', 'withdrawal'].map((type) => (
              <button
                key={type}
                onClick={() => setTypeFilter(type)}
                className={`rounded-md px-4 py-2 text-sm font-semibold transition-all duration-200 ${
                  typeFilter === type
                    ? 'bg-[var(--primary)] text-white shadow-sm'
                    : 'text-[var(--text-secondary)] hover:bg-[var(--surface-3)] hover:text-[var(--text-primary)]'
                }`}
              >
                {type === 'all' ? 'All' : actionLabels[type]}
              </button>
            ))}
          </div>
        </div>

        {rows.length === 0 ? (
          <p className="py-8 text-center text-sm text-[var(--text-secondary)]">
            No transactions match your search/filter.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--border)] bg-[var(--surface-2)]">
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
                {rows.map((t) => {
                  const typeColor = t.action === 'buy' || t.action === 'deposit'
                    ? 'text-[var(--status-good)]'
                    : 'text-[var(--status-serious)]'

                  return (
                    <tr
                      key={t.id}
                      className="border-b border-[var(--border)] transition-colors hover:bg-[var(--surface-2)]"
                    >
                      <td className="px-4 py-4 text-[var(--text-secondary)]">
                        {formatDate(t.date)}
                      </td>
                      <td className="px-4 py-4 font-semibold text-[var(--text-primary)]">
                        {t.ticker}
                      </td>
                      <td className="px-4 py-4 text-[var(--text-secondary)]">
                        {capitalize(t.assetType)}
                      </td>
                      <td className={`px-4 py-4 font-semibold ${typeColor}`}>
                        {actionLabels[t.action] ?? capitalize(t.action)}
                      </td>
                      <td className="px-4 py-4 text-right text-[var(--text-secondary)]">
                        {Number(t.quantity ?? 0).toLocaleString('en-US', { maximumFractionDigits: 2 })}
                      </td>
                      <td className="px-4 py-4 text-right text-[var(--text-secondary)]">
                        {formatCurrency(t.price)}
                      </td>
                      <td className="px-4 py-4 text-right font-semibold text-[var(--text-primary)]">
                        {formatCurrency(t.total)}
                      </td>
                      <td className="px-4 py-4 text-right text-[var(--text-secondary)]">
                        {t.useCash ? 'Yes' : 'No'}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}

        <p className="mt-4 text-right text-sm text-[var(--text-secondary)]">
          {rows.length} transaction{rows.length !== 1 ? 's' : ''}
        </p>
      </div>
    </div>
  )
}

export default TransactionHistoryPage
