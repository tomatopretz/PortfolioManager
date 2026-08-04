/** Full-panel error, used when a page has nothing to render because a fetch failed. */
function ErrorState({ title = 'Something went wrong', message }) {
  return (
    <div
      role="alert"
      className="rounded-xl border border-[var(--status-serious)] bg-[var(--surface-1)] p-6 shadow-[var(--shadow-sm)]"
    >
      <p className="font-semibold text-[var(--status-serious)]">{title}</p>
      {message && <p className="mt-1 text-sm text-[var(--text-secondary)]">{message}</p>}
    </div>
  )
}

/** Inline banner, used when data is on screen but the last action failed. */
export function ErrorBanner({ children }) {
  if (!children) return null
  return (
    <div
      role="alert"
      className="rounded-lg border border-[var(--status-serious)] bg-[var(--status-serious)]/10 px-4 py-3 text-sm font-semibold text-[var(--status-serious)]"
    >
      {children}
    </div>
  )
}

export default ErrorState
