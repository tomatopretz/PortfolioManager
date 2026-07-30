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
    <div className="flex gap-2 p-1 rounded-lg w-fit bg-gray-100">
      {ranges.map((range) => (
        <button
          key={range.key}
          onClick={() => onTimeRangeChange(range.key)}
          className={`px-4 py-2 rounded-md text-sm font-semibold transition-all duration-200 ${
            timeRange === range.key
              ? 'text-white bg-blue-600 shadow-sm'
              : 'text-gray-700 hover:text-gray-900 hover:bg-gray-200'
          }`}
        >
          {range.label}
        </button>
      ))}
    </div>
  )
}

export default TimeRangeFilter
