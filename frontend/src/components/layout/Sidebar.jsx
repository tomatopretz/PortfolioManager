import { NavLink } from 'react-router-dom'

// `icon` is the SVG path data for each destination, kept alongside the route it belongs to
// instead of being selected by a chain of `path === '/x' && ...` checks in the markup.
const NAV_ITEMS = [
  {
    path: '/',
    label: 'Dashboard',
    icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
  },
  { path: '/holdings', label: 'Holdings', icon: 'M13 10V3L4 14h7v7l9-11h-7z' },
  { path: '/transactions', label: 'Transactions', icon: '🧾' },
]

const linkClassName = ({ isActive }) =>
  `flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-semibold transition-all duration-200 ${
    isActive
      ? 'bg-[var(--primary)] text-white shadow-md'
      : 'text-[var(--text-secondary)] hover:bg-[var(--surface-2)] hover:text-[var(--text-primary)]'
  }`

function Sidebar() {
  return (
    <aside className="sticky top-0 flex h-screen w-64 flex-col border-r border-[var(--gridline)] bg-[var(--surface-1)]">
      <div className="mb-12 px-6 pt-8">
        <p className="font-display text-2xl font-bold text-[var(--primary)]">PM</p>
        <p className="mt-2 text-xs font-semibold tracking-widest text-[var(--text-secondary)]">
          PORTFOLIO
        </p>
      </div>

      <nav className="flex-1 space-y-1 px-4">
        {NAV_ITEMS.map((item) => (
          <NavLink key={item.path} to={item.path} className={linkClassName}>
            <svg
              className="h-5 w-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d={item.icon}
              />
            </svg>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-[var(--gridline)] px-6 pb-8 pt-6 text-xs font-semibold text-[var(--text-secondary)]">
        <p>Portfolio Manager</p>
        <p className="mt-1 text-[var(--text-muted)]">v1.0</p>
      </div>
    </aside>
  )
}

export default Sidebar
