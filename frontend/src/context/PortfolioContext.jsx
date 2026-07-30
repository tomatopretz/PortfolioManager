import { createContext, useContext } from 'react'
import { usePortfolio } from '../hooks/usePortfolio'

const PortfolioContext = createContext()

export const usePortfolioContext = () => {
  const context = useContext(PortfolioContext)
  if (!context) {
    throw new Error('usePortfolioContext must be used within PortfolioProvider')
  }
  return context
}

export const PortfolioProvider = ({ children }) => {
  const portfolio = usePortfolio()
  return (
    <PortfolioContext.Provider value={portfolio}>
      {children}
    </PortfolioContext.Provider>
  )
}
