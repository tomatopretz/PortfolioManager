function DashboardPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>
        Dashboard
      </h2>
      <div className="bg-white rounded-lg p-6 border border-[var(--gridline)]">
        <p style={{ color: 'var(--text-secondary)' }}>
          Dashboard content will be displayed here.
        </p>
      </div>
    </div>
  )
}

export default DashboardPage
