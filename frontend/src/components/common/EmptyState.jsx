function EmptyState({ title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--surface-1)] p-12 text-center shadow-[var(--shadow-sm)]">
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-[var(--primary)]/15">
        <svg className="h-6 w-6 text-[var(--primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      </div>
      <h3 className="mb-2 text-xl font-bold text-[var(--text-primary)]">
        {title}
      </h3>
      <p className="mb-6 max-w-sm text-[var(--text-secondary)]">
        {description}
      </p>
      {action && (
        <button
          onClick={action.onClick}
          className="rounded-lg bg-[var(--primary)] px-6 py-2 text-sm font-semibold text-white transition-all duration-200 hover:bg-[var(--primary-dark)] hover:shadow-md hover:-translate-y-0.5 active:translate-y-0"
        >
          {action.label}
        </button>
      )}
    </div>
  )
}

export default EmptyState
