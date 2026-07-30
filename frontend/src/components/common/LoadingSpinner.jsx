function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="h-8 w-8 rounded-full border-4 border-gray-200 border-t-blue-600 animate-spin" />
        <p className="text-sm font-semibold text-gray-600">
          Loading portfolio data...
        </p>
      </div>
    </div>
  )
}

export default LoadingSpinner
