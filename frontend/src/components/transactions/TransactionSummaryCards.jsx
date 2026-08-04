import StatTile from '../common/StatTile'

function TransactionSummaryCards({ transactions }) {
  const totalCount = transactions.length
  const buyCount = transactions.filter((t) => t.action === 'buy').length
  const sellCount = transactions.filter((t) => t.action === 'sell').length

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
      <StatTile label="Total Transactions" value={totalCount} format="count" />
      <StatTile label="Buys" value={buyCount} format="count" />
      <StatTile label="Sells" value={sellCount} format="count" />
    </div>
  )
}

export default TransactionSummaryCards
