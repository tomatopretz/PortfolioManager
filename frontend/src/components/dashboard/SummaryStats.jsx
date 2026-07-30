import StatTile from '../common/StatTile'

function SummaryStats({ totalValue, totalReturn, cashBalance }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatTile
        label="Total Portfolio Value"
        value={totalValue}
      />
      <StatTile
        label="Total Return"
        value={totalReturn.amount}
        deltaPercent={totalReturn.percent}
      />
      <StatTile
        label="Return %"
        value={totalReturn.percent}
        format="percent"
      />
      <StatTile
        label="Cash Balance"
        value={cashBalance}
      />
    </div>
  )
}

export default SummaryStats
