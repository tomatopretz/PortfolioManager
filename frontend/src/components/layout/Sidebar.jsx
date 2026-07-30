import { NavLink } from 'react-router-dom'

function Sidebar() {
  const navItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/holdings', label: 'Holdings', icon: '📈' },
    { path: '/performance', label: 'Performance', icon: '📉' },
  ]

  return (
    <aside className="w-64 h-screen flex flex-col border-r border-gray-200 bg-white sticky top-0">
      {/* Logo */}
      <div className="pt-8 px-6 mb-12">
        <h1 className="text-2xl font-bold text-blue-600">PM</h1>
        <p className="text-xs tracking-widest mt-2 font-semibold text-gray-600">
          PORTFOLIO
        </p>
      </div>

      {/* Navigation */}
      <nav className="space-y-1 flex-1 px-4">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-semibold transition-all duration-200 ${
                isActive
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-gray-600 hover:bg-gray-100'
              }`
            }
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {item.path === '/' && (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              )}
              {item.path === '/holdings' && (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              )}
              {item.path === '/performance' && (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              )}
            </svg>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="pb-8 px-6 border-t border-gray-200 pt-6 text-xs font-semibold text-gray-600">
        <p>Portfolio Manager</p>
        <p className="text-gray-400 mt-1">v1.0</p>
      </div>
    </aside>
  )
}

export default Sidebar
