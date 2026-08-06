import { useMemo, useState } from 'react'
import { usePortfolioContext } from '../context/PortfolioContext'
import Card from '../components/common/Card'
import EmptyState from '../components/common/EmptyState'
import ErrorState, { ErrorBanner } from '../components/common/ErrorState'
import LoadingSpinner from '../components/common/LoadingSpinner'
import SegmentedControl from '../components/common/SegmentedControl'
import HoldingsSummaryCards from '../components/holdings/HoldingsSummaryCards'
import HoldingsTable from '../components/holdings/HoldingsTable'
import { capitalize, pluralize } from '../utils/format'
import {
  getCostBasisPerShare,
  isCashItem,
  isZeroQuantity,
  normalizeAssetType,
} from '../utils/portfolio'

const ALL_TYPES = 'all'

const getSortValue = (item, key) =>
  key === 'costBasisPerShare' ? getCostBasisPerShare(item) : item[key]

const compareBy = (a, b, key) => {
  const left = getSortValue(a, key)
  const right = getSortValue(b, key)
  if (typeof left === 'string' || typeof right === 'string') {
    return String(left ?? '').localeCompare(String(right ?? ''))
  }
  return (left ?? 0) - (right ?? 0)
}

/**
 * Cash is pinned to the top and sold-out positions sink to the bottom, regardless of the
 * chosen sort column.
 */
const orderRows = (items, sort) => {
  const cashItem = items.find(isCashItem)
  const direction = sort.direction === 'asc' ? 1 : -1

  const rest = items
    .filter((item) => !isCashItem(item))
    .sort((a, b) => {
      const aEmpty = isZeroQuantity(a)
      const bEmpty = isZeroQuantity(b)
      if (aEmpty !== bEmpty) return aEmpty ? 1 : -1
      return direction * compareBy(a, b, sort.key)
    })

  return cashItem ? [cashItem, ...rest] : rest
}

function HoldingsPage() {
  const { items, itemsLoading, error, totalValue, highlights, toggleFavourite } = usePortfolioContext()
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState(ALL_TYPES)
  const [sort, setSort] = useState({ key: 'ticker', direction: 'asc' })

  const typeOptions = useMemo(() => {
    const types = new Set(items.map((item) => normalizeAssetType(item.assetType)).filter(Boolean))
    return [
      { value: ALL_TYPES, label: 'All' },
      ...Array.from(types)
        .sort()
        .map((type) => ({ value: type, label: capitalize(type) })),
    ]
  }, [items])

  const rows = useMemo(() => {
    const query = search.trim().toLowerCase()
    const filtered = items.filter((item) => {
      const matchesType =
        typeFilter === ALL_TYPES || normalizeAssetType(item.assetType) === typeFilter
      const matchesSearch = query === '' || String(item.ticker ?? '').toLowerCase().includes(query)
      return matchesType && matchesSearch
    })
    return orderRows(filtered, sort)
  }, [items, search, typeFilter, sort])

  const handleSort = (key) =>
    setSort((prev) =>
      prev.key === key
        ? { key, direction: prev.direction === 'asc' ? 'desc' : 'asc' }
        : { key, direction: 'asc' }
    )

  const heading = <h2 className="text-xl font-bold text-[var(--text-primary)]">Holdings</h2>

  if (itemsLoading && items.length === 0) {
    return <LoadingSpinner block />
  }

  if (error && items.length === 0) {
    return <ErrorState title="Error loading portfolio" message={error} />
  }

  if (items.length === 0) {
    return (
      <div className="space-y-6">
        {heading}
        <EmptyState
          title="No Holdings Yet"
          description="Once you add assets to your portfolio, they'll show up here."
        />
      </div>
    )
  }

  const holdingsCount = rows.filter((item) => !isCashItem(item) && !isZeroQuantity(item)).length

  return (
    <div className="space-y-6">
      {heading}

      <ErrorBanner>{error}</ErrorBanner>

      <HoldingsSummaryCards highlights={highlights} totalValue={totalValue} />

      <Card padding="p-8">
        <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search by ticker..."
            aria-label="Search holdings by ticker"
            className="w-full max-w-xs rounded-lg border border-[var(--border)] bg-[var(--surface-1)] px-4 py-2 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:border-[var(--primary)] focus:outline-none"
          />

          <SegmentedControl
            ariaLabel="Filter by asset type"
            options={typeOptions}
            value={typeFilter}
            onChange={setTypeFilter}
          />
        </div>

        {rows.length === 0 ? (
          <p className="py-8 text-center text-sm text-[var(--text-secondary)]">
            No holdings match your search/filter.
          </p>
        ) : (
          <HoldingsTable
            rows={rows}
            sort={sort}
            onSort={handleSort}
            onToggleFavourite={toggleFavourite}
          />
        )}

        <p className="mt-4 text-right text-sm text-[var(--text-secondary)]">
          {pluralize(holdingsCount, 'holding')}
        </p>
      </Card>
    </div>
  )
}

export default HoldingsPage
