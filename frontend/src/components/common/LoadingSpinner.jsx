function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-[var(--surface-3)] border-t-[var(--primary)]" />
        <p className="text-sm font-semibold text-[var(--text-secondary)]">
          Loading portfolio data...
        </p>
      </div>
    </div>
  )
}

export default LoadingSpinner
