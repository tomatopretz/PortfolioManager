import { NavLink } from 'react-router-dom'

function NavMenu() {
  return (
    <nav className="border-b border-[var(--gridline)] bg-[var(--surface-1)]">
      <div className="flex gap-8 px-6">
        <NavLink
          to="/"
          className={({ isActive }) =>
            `border-b-2 px-2 py-4 ${
              isActive
                ? 'border-[var(--series-1)] font-semibold text-[var(--text-primary)]'
                : 'border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
            }`
          }
        >
          Dashboard
        </NavLink>
        <NavLink
          to="/holdings"
          className={({ isActive }) =>
            `border-b-2 px-2 py-4 ${
              isActive
                ? 'border-[var(--series-1)] font-semibold text-[var(--text-primary)]'
                : 'border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
            }`
          }
        >
          Holdings
        </NavLink>
        <NavLink
          to="/analytics"
          className={({ isActive }) =>
            `border-b-2 px-2 py-4 ${
              isActive
                ? 'border-[var(--series-1)] font-semibold text-[var(--text-primary)]'
                : 'border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
            }`
          }
        >
          Analytics
        </NavLink>
      </div>
    </nav>
  )
}

export default NavMenu
