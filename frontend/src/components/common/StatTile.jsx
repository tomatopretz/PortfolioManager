function StatTile({ label, value, delta, deltaPercent, format = 'currency' }) {
  const deltaColor = delta >= 0 ? 'text-[var(--status-good)]' : 'text-[var(--status-serious)]'

  const formatValue = (val) => {
    if (format === 'currency') {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(val)
    }
    if (format === 'percent') {
      return `${val.toFixed(2)}%`
    }
    return val
  }

  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-1)] p-6 transition-all duration-200 hover:border-[var(--primary)] hover:shadow-[var(--shadow-md)]">
      <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
        {label}
      </p>
      <p className="mb-2 text-3xl font-bold text-[var(--text-primary)]">
        {formatValue(value)}
      </p>
      {delta !== undefined && (
        <p className={`text-sm font-semibold ${deltaColor}`}>
          {delta >= 0 ? '+' : ''}{formatValue(delta)}
          {deltaPercent !== undefined && ` (${deltaPercent >= 0 ? '+' : ''}${deltaPercent.toFixed(2)}%)`}
        </p>
      )}
    </div>
  )
}

export default StatTile
