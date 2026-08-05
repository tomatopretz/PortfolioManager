import { useEffect, useMemo, useState } from 'react'
import { usePortfolioContext } from '../context/PortfolioContext'
import { useAsyncResource } from '../hooks/useAsyncResource'
import { bulkRecordTransactions, downloadTransactionsCsv, getTransactions } from '../services'
import Button from '../components/common/Button'
import Card from '../components/common/Card'
import EmptyState from '../components/common/EmptyState'
import ErrorState from '../components/common/ErrorState'
import LoadingSpinner from '../components/common/LoadingSpinner'
import SegmentedControl from '../components/common/SegmentedControl'
import TransactionCsvImportModal from '../components/transactions/TransactionCsvImportModal'
import TransactionSummaryCards from '../components/transactions/TransactionSummaryCards'
import TransactionsTable from '../components/transactions/TransactionsTable'
import { ACTION_FILTER_OPTIONS, ALL_ACTIONS } from '../constants/transactions'
import { pluralize } from '../utils/format'
import { buildTransactionRows, compareTransactions } from '../utils/transactions'

function TransactionHistoryPage() {
  // Transactions are page-scoped rather than part of the portfolio context, but a trade made
  // from the header still invalidates them - hence the refetch on `dataVersion`.
  const { items, dataVersion, refreshAll } = usePortfolioContext()
  const { data: transactions, loading, error, load } = useAsyncResource(getTransactions, [])

  const [search, setSearch] = useState('')
  const [actionFilter, setActionFilter] = useState(ALL_ACTIONS)
  const [sort, setSort] = useState({ key: 'date', direction: 'desc' })
  const [importOpen, setImportOpen] = useState(false)

  useEffect(() => {
    load()
  }, [load, dataVersion])

  const allRows = useMemo(
    () => buildTransactionRows(transactions, items),
    [transactions, items]
  )

  const rows = useMemo(() => {
    const query = search.trim().toLowerCase()
    const direction = sort.direction === 'asc' ? 1 : -1

    return allRows
      .filter((row) => {
        const matchesAction = actionFilter === ALL_ACTIONS || row.action === actionFilter
        const matchesSearch = query === '' || row.ticker.toLowerCase().includes(query)
        return matchesAction && matchesSearch
      })
      .sort((a, b) => direction * compareTransactions(a, b, sort.key))
  }, [allRows, search, actionFilter, sort])

  const hasExportableRows = useMemo(
    () => allRows.some((row) => ['buy', 'sell', 'deposit', 'withdrawal'].includes(row.action)),
    [allRows]
  )

  const handleSort = (key) =>
    setSort((prev) =>
      prev.key === key
        ? { key, direction: prev.direction === 'asc' ? 'desc' : 'asc' }
        : { key, direction: 'asc' }
    )

  const handleExport = () => {
    downloadTransactionsCsv()
  }

  const handleImport = async (transactionPayloads) => {
    await bulkRecordTransactions(transactionPayloads)
    await refreshAll()
    await load()
  }

  const heading = (
    <h2 className="text-xl font-bold text-[var(--text-primary)]">Transaction History</h2>
  )

  const controls = (
    <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      <input
        type="search"
        value={search}
        onChange={(event) => setSearch(event.target.value)}
        placeholder="Search by ticker..."
        aria-label="Search transactions by ticker"
        className="w-full max-w-xs rounded-lg border border-[var(--border)] bg-[var(--surface-1)] px-4 py-2 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:border-[var(--primary)] focus:outline-none"
      />

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="flex gap-2">
          <Button variant="secondary" onClick={() => setImportOpen(true)}>
            Import CSV
          </Button>
          <Button variant="secondary" onClick={handleExport} disabled={!hasExportableRows}>
            Export CSV
          </Button>
        </div>

        <SegmentedControl
          ariaLabel="Filter by transaction type"
          options={ACTION_FILTER_OPTIONS}
          value={actionFilter}
          onChange={setActionFilter}
        />
      </div>
    </div>
  )

  if (loading && transactions.length === 0) {
    return <LoadingSpinner block />
  }

  if (error && transactions.length === 0) {
    return <ErrorState title="Error loading transactions" message={error} />
  }

  if (allRows.length === 0) {
    return (
      <div className="space-y-6">
        {heading}
        <Card padding="p-8">{controls}</Card>
        <EmptyState
          title="No Transactions Yet"
          description="Once you buy or sell an asset, it will show up here."
        />
        <TransactionCsvImportModal
          isOpen={importOpen}
          onClose={() => setImportOpen(false)}
          onImport={handleImport}
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {heading}

      <TransactionSummaryCards transactions={allRows} />

      <Card padding="p-8">
        <div className="mb-6">{controls}</div>

        {rows.length === 0 ? (
          <p className="py-8 text-center text-sm text-[var(--text-secondary)]">
            No transactions match your search/filter.
          </p>
        ) : (
          <TransactionsTable rows={rows} sort={sort} onSort={handleSort} />
        )}

        <p className="mt-4 text-right text-sm text-[var(--text-secondary)]">
          {pluralize(rows.length, 'transaction')}
        </p>
      </Card>

      <TransactionCsvImportModal
        isOpen={importOpen}
        onClose={() => setImportOpen(false)}
        onImport={handleImport}
      />
    </div>
  )
}

export default TransactionHistoryPage
