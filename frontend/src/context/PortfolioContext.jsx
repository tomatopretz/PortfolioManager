import { createContext, useContext } from 'react'
import { usePortfolio } from '../hooks/usePortfolio'

const PortfolioContext = createContext(null)
PortfolioContext.displayName = 'PortfolioContext'

/** Reads the shared portfolio state. Throws if used outside `PortfolioProvider`. */
export const usePortfolioContext = () => {
  const context = useContext(PortfolioContext)
  if (!context) {
    throw new Error('usePortfolioContext must be used within PortfolioProvider')
  }
  return context
}

export const PortfolioProvider = ({ children }) => (
  <PortfolioContext.Provider value={usePortfolio()}>{children}</PortfolioContext.Provider>
)
