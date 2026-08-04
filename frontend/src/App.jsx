import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom'
import { PortfolioProvider } from './context/PortfolioContext'
import AppLayout from './components/layout/AppLayout'
import DashboardPage from './pages/DashboardPage'
import HoldingsPage from './pages/HoldingsPage'
import TransactionHistoryPage from './pages/TransactionHistoryPage'

function App() {
  return (
    <PortfolioProvider>
      <Router>
        <Routes>
          <Route element={<AppLayout />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/holdings" element={<HoldingsPage />} />
            <Route path="/transactions" element={<TransactionHistoryPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </Router>
    </PortfolioProvider>
  )
}

export default App
