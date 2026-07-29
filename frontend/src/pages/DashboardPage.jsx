import { usePortfolioContext } from '../context/PortfolioContext'
import LoadingSpinner from '../components/common/LoadingSpinner'
import EmptyState from '../components/common/EmptyState'
import SummaryStats from '../components/dashboard/SummaryStats'
import AllocationPieChart from '../components/dashboard/AllocationPieChart'
import PerformanceChart from '../components/dashboard/PerformanceChart'
import TimeRangeFilter from '../components/dashboard/TimeRangeFilter'
import HoldingsPreview from '../components/dashboard/HoldingsPreview'

function DashboardPage() {
  const {
    items,
    performance,
    loading,
    error,
    timeRange,
    setTimeRange,
    getTotalValue,
    getCashBalance,
    getTotalReturn,
  } = usePortfolioContext()

  if (loading && items.length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner />
      </div>
    )
  }

  if (error && items.length === 0) {
    return (
      <div
        className="rounded-lg border p-6"
        style={{
          backgroundColor: 'var(--surface-1)',
          borderColor: 'var(--status-critical)',
        }}
      >
        <p style={{ color: 'var(--status-critical)' }} className="font-semibold">
          Error loading portfolio
        </p>
        <p style={{ color: 'var(--text-secondary)' }} className="text-sm mt-1">
          {error}
        </p>
      </div>
    )
  }

  const nonCashItems = items.filter((item) => item.assetType !== 'cash')

  if (nonCashItems.length === 0) {
    return (
      <div className="space-y-6">
        <h2 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>
          Dashboard
        </h2>
        <EmptyState
          title="No Holdings Yet"
          description="Start building your portfolio by adding your first stock or bond. Click the Buy button above to get started."
          action={{ label: 'Buy Asset', onClick: () => {} }}
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>
        Dashboard
      </h2>

      <SummaryStats
        totalValue={getTotalValue()}
        totalReturn={getTotalReturn()}
        cashBalance={getCashBalance()}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="space-y-4">
            <TimeRangeFilter
              timeRange={timeRange}
              onTimeRangeChange={setTimeRange}
            />
            {loading ? (
              <div
                className="rounded-lg border p-12 flex items-center justify-center h-96"
                style={{
                  backgroundColor: 'var(--surface-1)',
                  borderColor: 'var(--gridline)',
                }}
              >
                <LoadingSpinner />
              </div>
            ) : (
              <PerformanceChart data={performance} timeRange={timeRange} />
            )}
          </div>
        </div>

        <AllocationPieChart items={nonCashItems} />
      </div>

      {nonCashItems.length > 0 && <HoldingsPreview items={nonCashItems} />}
    </div>
  )
}

export default DashboardPage
