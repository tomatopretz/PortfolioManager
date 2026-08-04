import Card from './Card'
import { formatCurrency, formatPercent, formatQuantity } from '../../utils/format'
import { toneClass } from '../../utils/portfolio'

const FORMATTERS = {
  currency: (value) => formatCurrency(value, 0),
  percent: (value) => formatPercent(value),
  count: (value) => formatQuantity(value, 0),
  text: (value) => value,
}

function StatTile({ label, value, delta, deltaPercent, format = 'currency' }) {
  const formatValue = FORMATTERS[format] ?? FORMATTERS.text
  const hasDelta = delta != null
  const hasDeltaPercent = deltaPercent != null
  const tone = toneClass(hasDelta ? delta : deltaPercent)

  return (
    <Card padding="p-5" interactive>
      <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
        {label}
      </p>
      <p className="mb-2 text-2xl font-bold text-[var(--text-primary)]">{formatValue(value)}</p>
      {(hasDelta || hasDeltaPercent) && (
        <p className={`text-sm font-semibold ${tone}`}>
          {hasDelta && `${delta >= 0 ? '+' : ''}${formatValue(delta)}`}
          {hasDelta && hasDeltaPercent && ' '}
          {hasDeltaPercent &&
            (hasDelta
              ? `(${deltaPercent >= 0 ? '+' : ''}${formatPercent(deltaPercent)})`
              : `${deltaPercent >= 0 ? '+' : ''}${formatPercent(deltaPercent)}`)}
        </p>
      )}
    </Card>
  )
}

export default StatTile
