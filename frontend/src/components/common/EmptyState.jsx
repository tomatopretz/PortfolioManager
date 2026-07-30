function EmptyState({ title, description, action }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-12 flex flex-col items-center justify-center text-center shadow-sm">
      <div className="w-12 h-12 rounded-full flex items-center justify-center mb-4 bg-blue-100">
        <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      </div>
      <h3 className="text-xl font-bold text-gray-900 mb-2">
        {title}
      </h3>
      <p className="text-gray-600 mb-6 max-w-sm">
        {description}
      </p>
      {action && (
        <button
          onClick={action.onClick}
          className="px-6 py-2 rounded-lg text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 transition-all duration-200 hover:shadow-md hover:-translate-y-0.5 active:translate-y-0"
        >
          {action.label}
        </button>
      )}
    </div>
  )
}

export default EmptyState
