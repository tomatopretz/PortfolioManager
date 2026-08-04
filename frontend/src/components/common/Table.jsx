const ALIGN = {
  left: 'text-left',
  right: 'text-right',
}

/**
 * Thin table primitives. They exist purely to stop the same
 * `px-4 py-3 text-left font-semibold text-[var(--text-secondary)]` string being retyped in
 * every table, and to keep header/body alignment in sync.
 */
export function Table({ scrollable = false, children }) {
  const wrapper = scrollable
    ? 'max-h-[540px] overflow-y-auto overflow-x-auto'
    : 'overflow-x-auto'
  return (
    <div className={wrapper}>
      <table className="w-full text-sm">{children}</table>
    </div>
  )
}

export function Thead({ sticky = false, children }) {
  return (
    <thead>
      <tr
        className={`border-b border-[var(--border)] bg-[var(--surface-2)] ${
          sticky ? 'sticky top-0 z-10' : ''
        }`}
      >
        {children}
      </tr>
    </thead>
  )
}

export function Th({ align = 'left', onClick, sortDirection, children }) {
  const base = `px-4 py-3 font-semibold text-[var(--text-secondary)] ${ALIGN[align]}`

  if (!onClick) {
    return <th className={base}>{children}</th>
  }

  return (
    <th
      className={base}
      aria-sort={sortDirection ? (sortDirection === 'asc' ? 'ascending' : 'descending') : 'none'}
    >
      <button
        type="button"
        onClick={onClick}
        className={`w-full cursor-pointer select-none font-semibold hover:text-[var(--text-primary)] ${ALIGN[align]}`}
      >
        {children}
        {sortDirection && (sortDirection === 'asc' ? ' ▲' : ' ▼')}
      </button>
    </th>
  )
}

export function Tbody({ children }) {
  return <tbody>{children}</tbody>
}

export function Tr({ children }) {
  return (
    <tr className="border-b border-[var(--border)] transition-colors hover:bg-[var(--surface-2)]">
      {children}
    </tr>
  )
}

export function Td({ align = 'left', className = '', children }) {
  return <td className={`px-4 py-4 ${ALIGN[align]} ${className}`}>{children}</td>
}
