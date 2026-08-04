import { useState } from 'react'
import { usePortfolioContext } from '../context/PortfolioContext'
import Card from '../components/common/Card'
import EmptyState from '../components/common/EmptyState'
import ErrorState from '../components/common/ErrorState'
import LoadingSpinner from '../components/common/LoadingSpinner'
import AllocationPieChart from '../components/dashboard/AllocationPieChart'
import HoldingsPreview from '../components/dashboard/HoldingsPreview'
import PerformanceChart from '../components/dashboard/PerformanceChart'
import SummaryStats from '../components/dashboard/SummaryStats'
import TransactionModal from '../components/portfolio/TransactionModal'
import { getMarketValue, isTradableHolding } from '../utils/portfolio'

function DashboardPage() {
  const {
    items,
    performance,
    itemsLoading,
    performanceLoading,
    error,
    timeRange,
    setTimeRange,
    totalValue,
    cashBalance,
    totalReturn,
    buyAsset,
  } = usePortfolioContext()

  const [isAddAssetModalOpen, setIsAddAssetModalOpen] = useState(false)

  if (itemsLoading && items.length === 0) {
    return <LoadingSpinner block />
  }

  if (error && items.length === 0) {
    return <ErrorState title="Error loading portfolio" message={error} />
  }

  const allocationItems = items.filter((item) => getMarketValue(item) > 0)
  const hasHoldings = items.some(isTradableHolding)

  return (
    <>
      {hasHoldings ? (
        <div className="space-y-6">
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <div className="lg:col-span-1">
              <AllocationPieChart items={allocationItems} />
            </div>
            <div className="lg:col-span-2">
              {performanceLoading ? (
                <Card padding="p-8" className="flex h-96 items-center justify-center">
                  <LoadingSpinner />
                </Card>
              ) : (
                <PerformanceChart
                  data={performance}
                  timeRange={timeRange}
                  onTimeRangeChange={setTimeRange}
                />
              )}
            </div>
          </div>

          {/* Wait for the items fetch to fully resolve so holdings never render partially. */}
          {!itemsLoading && <HoldingsPreview items={items} />}

          <SummaryStats
            totalValue={totalValue}
            totalReturn={totalReturn}
            cashBalance={cashBalance}
          />
        </div>
      ) : (
        <EmptyState
          title="No Holdings Yet"
          description="Start building your portfolio by adding your first stock or bond. Click the Add Asset button in the header to get started."
          action={{ label: 'Add Asset', onClick: () => setIsAddAssetModalOpen(true) }}
        />
      )}

      <TransactionModal
        mode="buy"
        isOpen={isAddAssetModalOpen}
        onClose={() => setIsAddAssetModalOpen(false)}
        onSubmit={buyAsset}
      />
    </>
  )
}

export default DashboardPage
