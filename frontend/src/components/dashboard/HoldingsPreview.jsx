import { Link } from 'react-router-dom'

function HoldingsPreview({ items }) {
  const holdings = items
    .filter((item) => item.assetType !== 'cash')
    .sort((a, b) => b.marketValue - a.marketValue)

  if (holdings.length === 0) {
    return null
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-8 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-bold text-gray-900">
          Asset Holdings
        </h3>
        <Link
          to="/holdings"
          className="text-sm font-semibold text-blue-600 hover:text-blue-700 transition-colors"
        >
          View all →
        </Link>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              <th className="text-left py-3 px-4 font-semibold text-gray-700">
                Symbol
              </th>
              <th className="text-right py-3 px-4 font-semibold text-gray-700">
                Shares
              </th>
              <th className="text-right py-3 px-4 font-semibold text-gray-700">
                Current Price
              </th>
              <th className="text-right py-3 px-4 font-semibold text-gray-700">
                Cost Basis
              </th>
              <th className="text-right py-3 px-4 font-semibold text-gray-700">
                Market Value
              </th>
              <th className="text-right py-3 px-4 font-semibold text-gray-700">
                P/L
              </th>
            </tr>
          </thead>
          <tbody>
            {holdings.map((item) => {
              const gainLossColor = item.gainLoss >= 0 ? 'text-green-600' : 'text-red-600'

              return (
                <tr
                  key={item.id}
                  className="border-b border-gray-200 hover:bg-gray-50 transition-colors"
                >
                  <td className="py-4 px-4 font-semibold text-gray-900">
                    {item.ticker}
                  </td>
                  <td className="text-right py-4 px-4 text-gray-700">
                    {item.quantity.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                  </td>
                  <td className="text-right py-4 px-4 text-gray-700">
                    ${item.currentPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </td>
                  <td className="text-right py-4 px-4 text-gray-700">
                    ${item.costBasis.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </td>
                  <td className="text-right py-4 px-4 font-semibold text-gray-900">
                    ${item.marketValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </td>
                  <td className={`text-right py-4 px-4 font-semibold ${gainLossColor}`}>
                    ${item.gainLoss.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ({item.gainLossPercent.toFixed(2)}%)
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default HoldingsPreview
