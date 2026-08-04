import StatTile from '../common/StatTile'
import { countByAction } from '../../utils/transactions'

function TransactionSummaryCards({ transactions }) {
  const counts = countByAction(transactions)

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
      <StatTile label="Total Transactions" value={transactions.length} format="count" />
      <StatTile label="Buys" value={counts.buy ?? 0} format="count" />
      <StatTile label="Sells" value={counts.sell ?? 0} format="count" />
    </div>
  )
}

export default TransactionSummaryCards
