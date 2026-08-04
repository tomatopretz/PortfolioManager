import { NavLink } from 'react-router-dom'

function Sidebar() {
  const navItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/holdings', label: 'Holdings', icon: '📈' },
    { path: '/transactions', label: 'Transactions', icon: '🧾' },
  ]

  return (
    <aside className="sticky top-0 flex h-screen w-64 flex-col border-r border-[var(--gridline)] bg-[var(--surface-1)]">
      {/* Logo */}
      <div className="mb-12 px-6 pt-8">
        <h1 className="text-2xl font-bold text-[var(--primary)]">PM</h1>
        <p className="mt-2 text-xs font-semibold tracking-widest text-[var(--text-secondary)]">
          PORTFOLIO
        </p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-4">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-semibold transition-all duration-200 ${
                isActive
                  ? 'bg-[var(--primary)] text-white shadow-md'
                  : 'text-[var(--text-secondary)] hover:bg-[var(--surface-2)] hover:text-[var(--text-primary)]'
              }`
            }
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {item.path === '/' && (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              )}
              {item.path === '/holdings' && (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              )}
              {item.path === '/transactions' && (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              )}
            </svg>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-[var(--gridline)] px-6 pb-8 pt-6 text-xs font-semibold text-[var(--text-secondary)]">
        <p>Portfolio Manager</p>
        <p className="mt-1 text-[var(--text-muted)]">v1.0</p>
      </div>
    </aside>
  )
}

export default Sidebar
