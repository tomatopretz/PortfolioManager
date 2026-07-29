function EmptyState({ title, description, action }) {
  return (
    <div
      className="rounded-lg border p-12 flex flex-col items-center justify-center text-center"
      style={{
        backgroundColor: 'var(--surface-1)',
        borderColor: 'var(--gridline)',
      }}
    >
      <h3
        className="text-lg font-semibold mb-2"
        style={{ color: 'var(--text-primary)' }}
      >
        {title}
      </h3>
      <p style={{ color: 'var(--text-secondary)' }} className="mb-4 max-w-sm">
        {description}
      </p>
      {action && (
        <button
          onClick={action.onClick}
          className="px-4 py-2 rounded text-sm font-medium"
          style={{
            backgroundColor: 'var(--series-1)',
            color: 'white',
          }}
        >
          {action.label}
        </button>
      )}
    </div>
  )
}

export default EmptyState
