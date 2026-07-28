import { Outlet } from 'react-router-dom'
import Header from './Header'
import NavMenu from './NavMenu'

function AppLayout() {
  return (
    <div className="min-h-screen flex flex-col bg-[var(--surface-2)]">
      <Header />
      <NavMenu />
      <main className="flex-1 p-6">
        <Outlet />
      </main>
    </div>
  )
}

export default AppLayout
