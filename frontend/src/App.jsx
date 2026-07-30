import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { PortfolioProvider } from './context/PortfolioContext'
import AppLayout from './components/layout/AppLayout'
import DashboardPage from './pages/DashboardPage'
import HoldingsPage from './pages/HoldingsPage'
import PerformancePage from './pages/PerformancePage'

function App() {
  return (
    <PortfolioProvider>
      <Router>
        <Routes>
          <Route element={<AppLayout />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/holdings" element={<HoldingsPage />} />
            <Route path="/performance" element={<PerformancePage />} />
          </Route>
        </Routes>
      </Router>
    </PortfolioProvider>
  )
}

export default App
