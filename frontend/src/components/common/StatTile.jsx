function StatTile({ label, value, delta, deltaPercent, format = 'currency' }) {
  const deltaColor = delta >= 0 ? 'var(--status-good)' : 'var(--status-critical)'

  const formatValue = (val) => {
    if (format === 'currency') {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(val)
    }
    return val
  }

  return (
    <div
      className="rounded-lg border p-4"
      style={{
        backgroundColor: 'var(--surface-1)',
        borderColor: 'var(--gridline)',
      }}
    >
      <p style={{ color: 'var(--text-muted)' }} className="text-sm mb-2">
        {label}
      </p>
      <p
        className="text-3xl font-bold mb-1"
        style={{ color: 'var(--text-primary)' }}
      >
        {formatValue(value)}
      </p>
      {delta !== undefined && (
        <p className="text-sm" style={{ color: deltaColor }}>
          {delta >= 0 ? '+' : ''}{formatValue(delta)}
          {deltaPercent !== undefined && ` (${deltaPercent >= 0 ? '+' : ''}${deltaPercent.toFixed(2)}%)`}
        </p>
      )}
    </div>
  )
}

export default StatTile
