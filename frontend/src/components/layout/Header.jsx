import { usePortfolioContext } from '../../context/PortfolioContext'
import TransactionButton from '../portfolio/TransactionButton'
import RefreshButton from './RefreshButton'
import { formatCurrency, formatSignedCurrencyOrNA, formatSignedPercentOrNA } from '../../utils/format'
import { toneClass } from '../../utils/portfolio'

function HeaderStat({ label, value, className = '' }) {
  return (
    <div className="text-right">
      <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
        {label}
      </p>
      <p className={`text-xl font-bold ${className}`}>{value}</p>
    </div>
  )
}

function Header() {
  const { totalValue, cashBalance, totalReturn } = usePortfolioContext()

  return (
    <header className="w-full border-b border-[var(--gridline)] bg-[var(--surface-1)] shadow-[var(--shadow-sm)]">
      <div className="flex items-center justify-between px-6 py-5">
        <h1 className="text-3xl font-bold text-[var(--text-primary)]">Portfolio Manager</h1>

        <div className="flex items-center gap-8">
          <div className="flex gap-5">
            <HeaderStat
              label="Total Value"
              value={formatCurrency(totalValue, 0)}
              className="text-[var(--text-primary)]"
            />

            <div className="w-px bg-[var(--gridline)]" />

            <HeaderStat
              label="Cash Balance"
              value={formatCurrency(cashBalance, 0)}
              className="text-[var(--text-primary)]"
            />

            <div className="w-px bg-[var(--gridline)]" />

            <HeaderStat
              label="Total Return"
              value={`${formatSignedCurrencyOrNA(totalReturn.amount)} (${formatSignedPercentOrNA(totalReturn.percent)})`}
              className={toneClass(totalReturn.amount)}
            />
          </div>

          <div className="flex items-center gap-2.5">
            <RefreshButton />
            <TransactionButton mode="buy" />
            <TransactionButton mode="sell" />
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
