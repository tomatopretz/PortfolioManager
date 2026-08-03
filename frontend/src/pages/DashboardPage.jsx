import { useState } from 'react'
import { usePortfolioContext } from '../context/PortfolioContext'
import LoadingSpinner from '../components/common/LoadingSpinner'
import EmptyState from '../components/common/EmptyState'
import SummaryStats from '../components/dashboard/SummaryStats'
import AllocationPieChart from '../components/dashboard/AllocationPieChart'
import PerformanceChart from '../components/dashboard/PerformanceChart'
import TimeRangeFilter from '../components/dashboard/TimeRangeFilter'
import HoldingsPreview from '../components/dashboard/HoldingsPreview'
import AssetBreakdown from '../components/dashboard/AssetBreakdown'
import AddAssetModal from '../components/portfolio/AddAssetModal'

function DashboardPage() {
  const {
    items,
    performance,
    itemsLoading,
    performanceLoading,
    error,
    timeRange,
    setTimeRange,
    getTotalValue,
    getCashBalance,
    getTotalReturn,
    handleBuy,
  } = usePortfolioContext()

  const [isAddAssetModalOpen, setIsAddAssetModalOpen] = useState(false)

  if (itemsLoading && items.length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
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

  const allocationItems = items.filter((item) => Number(item.marketValue ?? 0) > 0)

  const nonCashItems = items.filter((item) => {
    const assetType = String(item.assetType || '').toLowerCase()
    const ticker = String(item.ticker || '').toUpperCase()
    return assetType !== 'cash' && Number(item.marketValue ?? 0) > 0
  })

  if (nonCashItems.length === 0) {
    return (
      <>
        <div className="space-y-8">
          <EmptyState
            title="No Holdings Yet"
            description="Start building your portfolio by adding your first stock or bond. Click the Add Asset button in the header to get started."
            action={{ label: 'Add Asset', onClick: () => setIsAddAssetModalOpen(true) }}
          />
        </div>

        <AddAssetModal
          isOpen={isAddAssetModalOpen}
          onClose={() => setIsAddAssetModalOpen(false)}
          onSubmit={handleBuy}
        />
      </>
    )
  }

  return (
    <>
      <div className="space-y-6">
        {/* Row 1: Pie Chart & Performance Chart */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <AllocationPieChart items={allocationItems} />
          </div>
          <div className="lg:col-span-2">
            {performanceLoading ? (
              <div className="flex h-96 items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--surface-1)] p-8 shadow-[var(--shadow-sm)]">
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

        {/* Row 2: Holdings Table - wait for the items fetch to fully resolve so holdings never render partially */}
        {!itemsLoading && nonCashItems.length > 0 && <HoldingsPreview items={nonCashItems} />}

        {/* Row 3: Summary Stats (4 cards) */}
        <SummaryStats
          totalValue={getTotalValue()}
          totalReturn={getTotalReturn()}
          cashBalance={getCashBalance()}
        />
      </div>

      <AddAssetModal
        isOpen={isAddAssetModalOpen}
        onClose={() => setIsAddAssetModalOpen(false)}
        onSubmit={handleBuy}
      />
    </>
  )
}

export default DashboardPage
