import { usePortfolioContext } from '../../context/PortfolioContext'

function Header() {
  const { getTotalValue, getTotalReturn } = usePortfolioContext()

  const totalValue = getTotalValue()
  const totalReturn = getTotalReturn()
  const isPositive = totalReturn.amount >= 0

  return (
    <header className="w-full bg-white border-b border-gray-200 shadow-sm">
      <div className="px-8 py-6 flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-gray-900">Portfolio Manager</h1>
        </div>

        <div className="flex items-center gap-12">
          {/* Stats */}
          <div className="flex gap-6">
            <div className="text-right">
              <p className="text-xs font-semibold uppercase tracking-wider text-gray-600 mb-1">
                Total Value
              </p>
              <p className="text-2xl font-bold text-gray-900">
                ${totalValue.toLocaleString('en-US', {
                  minimumFractionDigits: 0,
                  maximumFractionDigits: 0,
                })}
              </p>
            </div>

            <div className="w-px bg-gray-200" />

            <div className="text-right">
              <p className="text-xs font-semibold uppercase tracking-wider text-gray-600 mb-1">
                Total Return
              </p>
              <p className={`text-2xl font-bold ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                {isPositive ? '+' : ''}{totalReturn.amount >= 0 ? '' : ''}{totalReturn.amount.toLocaleString('en-US', {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })} ({isPositive ? '+' : ''}{totalReturn.percent.toFixed(2)}%)
              </p>
            </div>
          </div>

          {/* Buttons */}
          <div className="flex gap-3">
            <button className="px-6 py-2 font-semibold text-sm rounded-lg text-white bg-blue-600 hover:bg-blue-700 transition-all duration-200 hover:shadow-md hover:-translate-y-0.5 active:translate-y-0">
              Add Asset
            </button>
            <button className="px-6 py-2 font-semibold text-sm rounded-lg text-gray-700 bg-gray-100 border border-gray-300 hover:bg-gray-200 transition-all duration-200 hover:shadow-md hover:-translate-y-0.5 active:translate-y-0">
              Sell Asset
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
