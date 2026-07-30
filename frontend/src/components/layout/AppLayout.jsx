import { Outlet } from 'react-router-dom'
import Header from './Header'
import Sidebar from './Sidebar'

function AppLayout() {
  return (
    <div className="min-h-screen flex bg-[var(--bg-main)]">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 overflow-auto bg-[var(--bg-main)]">
          <div className="p-6 w-full">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}

export default AppLayout
