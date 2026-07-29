function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center">
      <div className="flex flex-col items-center gap-3">
        <div
          className="h-8 w-8 rounded-full border-4 border-transparent animate-spin"
          style={{
            borderTopColor: 'var(--series-1)',
            borderRightColor: 'var(--series-2)',
          }}
        />
        <p style={{ color: 'var(--text-muted)' }} className="text-sm">
          Loading portfolio data...
        </p>
      </div>
    </div>
  )
}

export default LoadingSpinner
