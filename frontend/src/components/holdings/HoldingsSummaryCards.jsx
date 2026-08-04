import Card from '../common/Card'
import StatTile from '../common/StatTile'
import {
  formatCurrency,
  formatPercent,
  formatSignedCurrencyOrNA,
  formatSignedPercentOrNA,
} from '../../utils/format'
import { extremeBy, isCashItem, toneClass } from '../../utils/portfolio'

// label + which metric decides the winner + how that metric reads on the card.
const CARDS = [
  { label: 'Largest Position', key: 'marketValue', mode: 'max', metric: 'share' },
  { label: 'Top Earner ($)', key: 'gainLoss', mode: 'max', metric: 'currency' },
  { label: 'Top Earner (%)', key: 'gainLossPercent', mode: 'max', metric: 'percent' },
  { label: 'Worst Earner ($)', key: 'gainLoss', mode: 'min', metric: 'currency' },
  { label: 'Worst Earner (%)', key: 'gainLossPercent', mode: 'min', metric: 'percent' },
]

function PositionCard({ label, ticker, metricText, metricTone }) {
  return (
    <Card padding="p-5" interactive>
      <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
        {label}
      </p>
      <p className="mb-2 text-2xl font-bold text-[var(--text-primary)]">{ticker ?? '—'}</p>
      {metricText && <p className={`text-sm font-semibold ${metricTone}`}>{metricText}</p>}
    </Card>
  )
}

function HoldingsSummaryCards({ items, totalValue }) {
  const nonCash = items.filter((item) => !isCashItem(item))

  const describe = ({ key, mode, metric }) => {
    const item = extremeBy(nonCash, key, mode)
    if (!item) return { ticker: null, metricText: null, metricTone: '' }

    if (metric === 'share') {
      const share = totalValue > 0 ? ((item.marketValue ?? 0) / totalValue) * 100 : 0
      return {
        ticker: item.ticker,
        metricText: `${formatCurrency(item.marketValue)} (${formatPercent(share)} of portfolio)`,
        metricTone: 'text-[var(--text-secondary)]',
      }
    }

    const value = item[key]
    return {
      ticker: item.ticker,
      metricText:
        metric === 'currency'
          ? formatSignedCurrencyOrNA(value)
          : formatSignedPercentOrNA(value),
      metricTone: toneClass(value),
    }
  }

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
      {CARDS.map((card) => (
        <PositionCard key={card.label} label={card.label} {...describe(card)} />
      ))}
      <StatTile label="Total Market Value" value={totalValue} />
    </div>
  )
}

export default HoldingsSummaryCards
