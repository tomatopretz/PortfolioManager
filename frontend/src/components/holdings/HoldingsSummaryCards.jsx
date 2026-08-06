import Card from '../common/Card'
import StatTile from '../common/StatTile'
import {
  formatCurrency,
  formatPercent,
  formatSignedCurrencyOrNA,
  formatSignedPercentOrNA,
} from '../../utils/format'
import { toneClass } from '../../utils/portfolio'

// label + which backend highlight fills the card + how its metric reads.
const CARDS = [
  { label: 'Largest Position', highlight: 'largestPosition', metric: 'share' },
  { label: 'Top Earner ($)', highlight: 'topEarnerByAmount', metric: 'currency', valueKey: 'gainLoss' },
  { label: 'Top Earner (%)', highlight: 'topEarnerByPercent', metric: 'percent', valueKey: 'gainLossPercent' },
  { label: 'Worst Earner ($)', highlight: 'worstEarnerByAmount', metric: 'currency', valueKey: 'gainLoss' },
  { label: 'Worst Earner (%)', highlight: 'worstEarnerByPercent', metric: 'percent', valueKey: 'gainLossPercent' },
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

function HoldingsSummaryCards({ highlights, totalValue }) {
  const describe = ({ highlight, metric, valueKey }) => {
    const item = highlights[highlight]
    if (!item) return { ticker: null, metricText: null, metricTone: '' }

    if (metric === 'share') {
      const share = totalValue > 0 ? ((item.marketValue ?? 0) / totalValue) * 100 : 0
      return {
        ticker: item.ticker,
        metricText: `${formatCurrency(item.marketValue)} (${formatPercent(share)} of portfolio)`,
        metricTone: 'text-[var(--text-secondary)]',
      }
    }

    const value = item[valueKey]
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
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
      {CARDS.map((card) => (
        <PositionCard key={card.label} label={card.label} {...describe(card)} />
      ))}
    </div>
  )
}

export default HoldingsSummaryCards
