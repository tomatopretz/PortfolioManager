import StatTile from '../common/StatTile'

function SummaryStats({ totalValue, totalReturn, cashBalance }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <StatTile
        label="Total Portfolio Value"
        value={totalValue}
        delta={totalReturn.amount}
        deltaPercent={totalReturn.percent}
      />
      <StatTile
        label="Total Return"
        value={totalReturn.amount}
        deltaPercent={totalReturn.percent}
      />
      <StatTile
        label="Cash Balance"
        value={cashBalance}
      />
    </div>
  )
}

export default SummaryStats
