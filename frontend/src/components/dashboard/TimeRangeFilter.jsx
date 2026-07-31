function TimeRangeFilter({ timeRange, onTimeRangeChange }) {
  const ranges = [
    { key: '1d', label: '1D' },
    { key: '1w', label: '1W' },
    { key: '1m', label: '1M' },
    { key: '6m', label: '6M' },
    { key: '1y', label: '1Y' },
    { key: 'all', label: 'All' },
  ]

  return (
    <div className="flex w-fit gap-2 rounded-lg bg-[var(--surface-2)] p-1">
      {ranges.map((range) => (
        <button
          key={range.key}
          onClick={() => onTimeRangeChange(range.key)}
          className={`rounded-md px-4 py-2 text-sm font-semibold transition-all duration-200 ${
            timeRange === range.key
              ? 'bg-[var(--primary)] text-white shadow-sm'
              : 'text-[var(--text-secondary)] hover:bg-[var(--surface-3)] hover:text-[var(--text-primary)]'
          }`}
        >
          {range.label}
        </button>
      ))}
    </div>
  )
}

export default TimeRangeFilter
