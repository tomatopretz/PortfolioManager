import { usePortfolioContext } from '../../context/PortfolioContext'

function Header() {
  const { getTotalValue, getTotalReturn } = usePortfolioContext()

  const totalValue = getTotalValue()
  const totalReturn = getTotalReturn()
  const isPositive = totalReturn.amount >= 0

  return (
    <header className="w-full border-b border-[var(--gridline)] bg-[var(--surface-1)] shadow-[var(--shadow-sm)]">
      <div className="flex items-center justify-between px-8 py-6">
        <div>
          <h1 className="text-4xl font-bold text-[var(--text-primary)]">Portfolio Manager</h1>
        </div>

        <div className="flex items-center gap-12">
          {/* Stats */}
          <div className="flex gap-6">
            <div className="text-right">
              <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
                Total Value
              </p>
              <p className="text-2xl font-bold text-[var(--text-primary)]">
                ${totalValue.toLocaleString('en-US', {
                  minimumFractionDigits: 0,
                  maximumFractionDigits: 0,
                })}
              </p>
            </div>

            <div className="w-px bg-[var(--gridline)]" />

            <div className="text-right">
              <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
                Total Return
              </p>
              <p className={`text-2xl font-bold ${isPositive ? 'text-[var(--status-good)]' : 'text-[var(--status-serious)]'}`}>
                {isPositive ? '+' : ''}{totalReturn.amount.toLocaleString('en-US', {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })} ({isPositive ? '+' : ''}{totalReturn.percent.toFixed(2)}%)
              </p>
            </div>
          </div>

          {/* Buttons */}
          <div className="flex gap-3">
            <button className="rounded-lg bg-[var(--primary)] px-6 py-2 text-sm font-semibold text-white transition-all duration-200 hover:bg-[var(--primary-dark)] hover:shadow-md hover:-translate-y-0.5 active:translate-y-0">
              Add Asset
            </button>
            <button className="rounded-lg border border-[var(--border)] bg-[var(--surface-2)] px-6 py-2 text-sm font-semibold text-[var(--text-primary)] transition-all duration-200 hover:bg-[var(--surface-3)] hover:shadow-md hover:-translate-y-0.5 active:translate-y-0">
              Sell Asset
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
