function StatTile({ label, value, delta, deltaPercent, format = 'currency' }) {
  const deltaColor = delta >= 0 ? 'text-green-600' : 'text-red-600'

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
    <div className="bg-white rounded-xl border border-gray-200 p-6 transition-all duration-200 hover:border-blue-400 hover:shadow-lg">
      <p className="text-xs font-semibold uppercase tracking-wider text-gray-600 mb-3">
        {label}
      </p>
      <p className="text-3xl font-bold text-gray-900 mb-2">
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
