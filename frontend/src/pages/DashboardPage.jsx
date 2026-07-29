import { usePortfolioContext } from '../context/PortfolioContext'
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
        <p style={{ color: 'var(--text-muted)' }}>Loading portfolio data...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-lg border p-6 bg-red-50 border-red-200">
        <p style={{ color: 'var(--status-critical)' }}>Error loading portfolio: {error}</p>
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
            <PerformanceChart data={performance} timeRange={timeRange} />
          </div>
        </div>

        <AllocationPieChart items={items} />
      </div>

      <HoldingsPreview items={items} />
    </div>
  )
}

export default DashboardPage
