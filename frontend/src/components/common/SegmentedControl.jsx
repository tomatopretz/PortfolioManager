/**
 * Pill-style single-choice control, shared by the chart time-range picker and the holdings
 * asset-type filter. `options` is `{ value, label }[]`.
 */
function SegmentedControl({ options, value, onChange, ariaLabel }) {
  return (
    <div
      role="group"
      aria-label={ariaLabel}
      className="flex w-fit flex-wrap gap-2 rounded-lg bg-[var(--surface-2)] p-1"
    >
      {options.map((option) => {
        const isActive = option.value === value
        return (
          <button
            key={option.value}
            type="button"
            aria-pressed={isActive}
            onClick={() => onChange(option.value)}
            className={`rounded-md px-4 py-2 text-sm font-semibold transition-all duration-200 ${
              isActive
                ? 'bg-[var(--primary)] text-white shadow-sm'
                : 'text-[var(--text-secondary)] hover:bg-[var(--surface-3)] hover:text-[var(--text-primary)]'
            }`}
          >
            {option.label}
          </button>
        )
      })}
    </div>
  )
}

export default SegmentedControl
