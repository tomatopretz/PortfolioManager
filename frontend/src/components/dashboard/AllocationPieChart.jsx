import { useMemo, useState } from 'react'
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import Button from '../common/Button'
import Card from '../common/Card'
import { Table, Tbody, Td, Th, Thead, Tr } from '../common/Table'
import { chartColorAt } from '../../constants/portfolio'
import { capitalize, formatCurrency } from '../../utils/format'
import { getMarketValue, isCashItem, normalizeAssetType } from '../../utils/portfolio'

/** Rolls holdings up into one slice per asset type, largest first. */
const buildAllocation = (items) => {
  const totalsByType = new Map()

  items.forEach((item) => {
    if (getMarketValue(item) <= 0) return
    const key = isCashItem(item) ? 'cash' : normalizeAssetType(item.assetType) || 'other'
    totalsByType.set(key, (totalsByType.get(key) ?? 0) + getMarketValue(item))
  })

  const slices = Array.from(totalsByType, ([assetType, value]) => ({
    assetType,
    name: capitalize(assetType),
    value: Math.round(value * 100) / 100,
  })).sort((a, b) => b.value - a.value)

  const total = slices.reduce((sum, slice) => sum + slice.value, 0)

  return {
    total,
    slices: slices.map((slice) => ({
      ...slice,
      percent: total > 0 ? (slice.value / total) * 100 : 0,
    })),
  }
}

// Declared at module scope: an inline component identity changes every render, which makes
// recharts tear down and remount the tooltip.
function AllocationTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const { name, value, percent } = payload[0].payload
  return (
    <div className="rounded border border-[var(--border)] bg-[var(--surface-1)] p-2 text-sm shadow-[var(--shadow-lg)]">
      <p className="font-semibold text-[var(--text-primary)]">{name}</p>
      <p className="text-[var(--text-secondary)]">{formatCurrency(value)}</p>
      <p className="text-xs text-[var(--text-muted)]">{percent.toFixed(1)}% of portfolio</p>
    </div>
  )
}

function ColorSwatch({ index }) {
  return (
    <span
      className="inline-block h-3 w-3 shrink-0 rounded-full"
      style={{ backgroundColor: chartColorAt(index) }}
    />
  )
}

function AllocationPieChart({ items }) {
  const [showTable, setShowTable] = useState(false)
  const { slices } = useMemo(() => buildAllocation(items), [items])

  if (slices.length === 0) {
    return (
      <Card padding="p-8" className="flex h-96 items-center justify-center">
        <p className="font-semibold text-[var(--text-secondary)]">No allocation data available</p>
      </Card>
    )
  }

  return (
    <Card className="h-full">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-bold text-[var(--text-primary)]">Asset Allocation</h3>
        <Button variant="outline" size="sm" onClick={() => setShowTable((current) => !current)}>
          {showTable ? 'Show Chart' : 'Show Table'}
        </Button>
      </div>

      {showTable ? (
        <Table>
          <Thead>
            <Th>Asset Type</Th>
            <Th align="right">Value</Th>
            <Th align="right">% of Portfolio</Th>
          </Thead>
          <Tbody>
            {slices.map((slice, index) => (
              <Tr key={slice.assetType}>
                <Td>
                  <div className="flex items-center gap-3">
                    <ColorSwatch index={index} />
                    <span className="text-[var(--text-primary)]">{slice.name}</span>
                  </div>
                </Td>
                <Td align="right" className="font-semibold text-[var(--text-primary)]">
                  {formatCurrency(slice.value)}
                </Td>
                <Td align="right" className="text-[var(--text-secondary)]">
                  {slice.percent.toFixed(1)}%
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      ) : (
        <>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={slices} cx="50%" cy="50%" outerRadius={78} dataKey="value" labelLine={false}>
                {slices.map((slice, index) => (
                  <Cell key={slice.assetType} fill={chartColorAt(index)} />
                ))}
              </Pie>
              <Tooltip content={<AllocationTooltip />} />
            </PieChart>
          </ResponsiveContainer>

          <div className="mt-2 flex flex-wrap gap-x-4 gap-y-2">
            {slices.map((slice, index) => (
              <div key={slice.assetType} className="flex items-center gap-2 text-sm">
                <ColorSwatch index={index} />
                <span className="text-[var(--text-secondary)]">{slice.name}</span>
                <span className="font-semibold text-[var(--text-primary)]">
                  {slice.percent.toFixed(1)}% ({formatCurrency(slice.value, 0)})
                </span>
              </div>
            ))}
          </div>
        </>
      )}
    </Card>
  )
}

export default AllocationPieChart
