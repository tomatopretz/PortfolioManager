import { NavLink } from 'react-router-dom'

function NavMenu() {
  return (
    <nav className="bg-white border-b border-[var(--gridline)]">
      <div className="px-6 flex gap-8">
        <NavLink
          to="/"
          className={({ isActive }) =>
            `py-4 px-2 border-b-2 ${
              isActive
                ? 'border-[var(--series-1)] font-semibold'
                : 'border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
            }`
          }
        >
          Dashboard
        </NavLink>
        <NavLink
          to="/holdings"
          className={({ isActive }) =>
            `py-4 px-2 border-b-2 ${
              isActive
                ? 'border-[var(--series-1)] font-semibold'
                : 'border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
            }`
          }
        >
          Holdings
        </NavLink>
        <NavLink
          to="/analytics"
          className={({ isActive }) =>
            `py-4 px-2 border-b-2 ${
              isActive
                ? 'border-[var(--series-1)] font-semibold'
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
