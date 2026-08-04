/** `block` reserves the same height as the panel it replaces, so layout doesn't jump. */
function LoadingSpinner({ block = false, label = 'Loading portfolio data...' }) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={`flex items-center justify-center ${block ? 'h-96 w-full' : ''}`}
    >
      <div className="flex flex-col items-center gap-4">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-[var(--surface-3)] border-t-[var(--primary)]" />
        <p className="text-sm font-semibold text-[var(--text-secondary)]">{label}</p>
      </div>
    </div>
  )
}

export default LoadingSpinner
