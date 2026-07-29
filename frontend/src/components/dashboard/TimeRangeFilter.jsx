function TimeRangeFilter({ timeRange, onTimeRangeChange }) {
  const ranges = [
    { key: '1w', label: '1W' },
    { key: '1m', label: '1M' },
    { key: '3m', label: '3M' },
    { key: 'ytd', label: 'YTD' },
    { key: '1y', label: '1Y' },
    { key: 'all', label: 'All' },
  ]

  return (
    <div className="flex gap-2">
      {ranges.map((range) => (
        <button
          key={range.key}
          onClick={() => onTimeRangeChange(range.key)}
          className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
            timeRange === range.key
              ? 'bg-[var(--series-1)] text-white'
              : 'bg-[var(--surface-2)] text-[var(--text-secondary)] hover:bg-[var(--gridline)]'
          }`}
        >
          {range.label}
        </button>
      ))}
    </div>
  )
}

export default TimeRangeFilter
