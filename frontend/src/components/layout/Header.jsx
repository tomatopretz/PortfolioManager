import { usePortfolioContext } from '../../context/PortfolioContext'
import AddAssetButton from '../portfolio/AddAssetButton'
import DeleteAssetButton from '../portfolio/DeleteAssetButton'
import { formatCurrency, formatSignedCurrencyOrNA, formatSignedPercentOrNA } from '../../utils/format'

function Header() {
  const { getTotalValue, getTotalReturn } = usePortfolioContext()

  const totalValue = getTotalValue()
  const totalReturn = getTotalReturn()
  const isPositive = totalReturn.amount >= 0

  return (
    <header className="w-full border-b border-[var(--gridline)] bg-[var(--surface-1)] shadow-[var(--shadow-sm)]">
      <div className="flex items-center justify-between px-6 py-5">
        <div>
          <h1 className="text-3xl font-bold text-[var(--text-primary)]">Portfolio Manager</h1>
        </div>

        <div className="flex items-center gap-8">
          {/* Stats */}
          <div className="flex gap-5">
            <div className="text-right">
              <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
                Total Value
              </p>
              <p className="text-xl font-bold text-[var(--text-primary)]">
                {formatCurrency(totalValue, 0)}
              </p>
            </div>

            <div className="w-px bg-[var(--gridline)]" />

            <div className="text-right">
              <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
                Total Return
              </p>
              <p className={`text-xl font-bold ${isPositive ? 'text-[var(--status-good)]' : 'text-[var(--status-serious)]'}`}>
                {formatSignedCurrencyOrNA(totalReturn.amount)} ({formatSignedPercentOrNA(totalReturn.percent)})
              </p>
            </div>
          </div>

          {/* Buttons */}
          <div className="flex gap-2.5">
            <AddAssetButton />
            <DeleteAssetButton />
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
