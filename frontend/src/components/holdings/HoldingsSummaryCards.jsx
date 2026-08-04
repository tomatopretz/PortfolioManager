import StatTile from '../common/StatTile'
import { formatCurrency } from '../../utils/format'

const bestBy = (items, key) =>
  items.reduce((best, item) => ((item[key] ?? -Infinity) > (best?.[key] ?? -Infinity) ? item : best), null)

const worstBy = (items, key) =>
  items.reduce((worst, item) => ((item[key] ?? Infinity) < (worst?.[key] ?? Infinity) ? item : worst), null)

function PositionCard({ label, item, metricText, metricColor }) {
  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-1)] p-5 transition-all duration-200 hover:border-[var(--primary)] hover:shadow-[var(--shadow-md)]">
      <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
        {label}
      </p>
      <p className="mb-2 text-2xl font-bold text-[var(--text-primary)]">
        {item ? item.ticker : '—'}
      </p>
      {metricText && (
        <p className={`text-sm font-semibold ${metricColor}`}>
          {metricText}
        </p>
      )}
    </div>
  )
}

function HoldingsSummaryCards({ items, totalValue }) {
  const nonCash = items.filter((item) => String(item.assetType || '').toLowerCase() !== 'cash')

  const largestPosition = bestBy(nonCash, 'marketValue')
  const topEarnerDollar = bestBy(nonCash, 'gainLoss')
  const topEarnerPercent = bestBy(nonCash, 'gainLossPercent')
  const worstEarnerDollar = worstBy(nonCash, 'gainLoss')
  const worstEarnerPercent = worstBy(nonCash, 'gainLossPercent')
  const largestPositionPercent =
    largestPosition && totalValue > 0 ? ((largestPosition.marketValue ?? 0) / totalValue) * 100 : 0

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
      <PositionCard
        label="Largest Position"
        item={largestPosition}
        metricColor="text-[var(--text-secondary)]"
        metricText={
          largestPosition &&
          `${formatCurrency(largestPosition.marketValue)} (${largestPositionPercent.toFixed(2)}% of portfolio)`
        }
      />

      <PositionCard
        label="Top Earner ($)"
        item={topEarnerDollar}
        metricColor={
          topEarnerDollar && topEarnerDollar.gainLoss >= 0
            ? 'text-[var(--status-good)]'
            : 'text-[var(--status-serious)]'
        }
        metricText={
          topEarnerDollar && `${topEarnerDollar.gainLoss >= 0 ? '+' : ''}${formatCurrency(topEarnerDollar.gainLoss)}`
        }
      />

      <PositionCard
        label="Top Earner (%)"
        item={topEarnerPercent}
        metricColor={
          topEarnerPercent && topEarnerPercent.gainLossPercent >= 0
            ? 'text-[var(--status-good)]'
            : 'text-[var(--status-serious)]'
        }
        metricText={
          topEarnerPercent &&
          `${topEarnerPercent.gainLossPercent >= 0 ? '+' : ''}${topEarnerPercent.gainLossPercent.toFixed(2)}%`
        }
      />

      <PositionCard
        label="Worst Earner ($)"
        item={worstEarnerDollar}
        metricColor={
          worstEarnerDollar && worstEarnerDollar.gainLoss >= 0
            ? 'text-[var(--status-good)]'
            : 'text-[var(--status-serious)]'
        }
        metricText={
          worstEarnerDollar && `${worstEarnerDollar.gainLoss >= 0 ? '+' : ''}${formatCurrency(worstEarnerDollar.gainLoss)}`
        }
      />

      <PositionCard
        label="Worst Earner (%)"
        item={worstEarnerPercent}
        metricColor={
          worstEarnerPercent && worstEarnerPercent.gainLossPercent >= 0
            ? 'text-[var(--status-good)]'
            : 'text-[var(--status-serious)]'
        }
        metricText={
          worstEarnerPercent &&
          `${worstEarnerPercent.gainLossPercent >= 0 ? '+' : ''}${worstEarnerPercent.gainLossPercent.toFixed(2)}%`
        }
      />

      <StatTile label="Total Market Value" value={totalValue} />
    </div>
  )
}

export default HoldingsSummaryCards
