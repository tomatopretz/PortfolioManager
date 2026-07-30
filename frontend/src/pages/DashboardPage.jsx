import { usePortfolioContext } from '../context/PortfolioContext'
import LoadingSpinner from '../components/common/LoadingSpinner'
import EmptyState from '../components/common/EmptyState'
import SummaryStats from '../components/dashboard/SummaryStats'
import AllocationPieChart from '../components/dashboard/AllocationPieChart'
import PerformanceChart from '../components/dashboard/PerformanceChart'
import TimeRangeFilter from '../components/dashboard/TimeRangeFilter'
import HoldingsPreview from '../components/dashboard/HoldingsPreview'
import AssetBreakdown from '../components/dashboard/AssetBreakdown'

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
      <div className="bg-white rounded-xl border border-red-300 p-6 shadow-sm">
        <p className="text-red-700 font-semibold">
          Error loading portfolio
        </p>
        <p className="text-gray-700 text-sm mt-1">
          {error}
        </p>
      </div>
    )
  }

  const nonCashItems = items.filter((item) => item.assetType !== 'cash')

  if (nonCashItems.length === 0) {
    return (
      <div className="space-y-8">
        <EmptyState
          title="No Holdings Yet"
          description="Start building your portfolio by adding your first stock or bond. Click the Add Asset button in the header to get started."
          action={{ label: 'Add Asset', onClick: () => {} }}
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Row 1: Pie Chart & Performance Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <AllocationPieChart items={nonCashItems} />
        </div>
        <div className="lg:col-span-2">
          {loading ? (
            <div className="bg-white rounded-xl border border-gray-200 p-8 flex items-center justify-center h-96 shadow-sm">
              <LoadingSpinner />
            </div>
          ) : (
            <PerformanceChart
              data={performance}
              timeRange={timeRange}
              onTimeRangeChange={setTimeRange}
            />
          )}
        </div>
      </div>

      {/* Row 2: Holdings Table */}
      {nonCashItems.length > 0 && <HoldingsPreview items={nonCashItems} />}

      {/* Row 3: Summary Stats (4 cards) */}
      <SummaryStats
        totalValue={getTotalValue()}
        totalReturn={getTotalReturn()}
        cashBalance={getCashBalance()}
      />
    </div>
  )
}

export default DashboardPage
