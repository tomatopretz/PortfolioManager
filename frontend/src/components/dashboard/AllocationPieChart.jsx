import { useMemo, useState } from 'react'
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import Button from '../common/Button'
import Card from '../common/Card'
import { Table, Tbody, Td, Th, Thead, Tr } from '../common/Table'
import { chartColorAt } from '../../constants/portfolio'
import { capitalize, formatCurrency } from '../../utils/format'

// Backend sends { assetType, marketValue, percent } slices, already grouped and sorted largest
// first; this just adds the display name/value fields recharts expects.
const toSlices = (allocation) =>
  allocation.map((slice) => ({ ...slice, name: capitalize(slice.assetType), value: slice.marketValue }))

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

/**
 * Sits at the far end of each slice's leader line. Recharts hands us that endpoint (`x`/`y`) and
 * the matching `textAnchor`, so the text always reads outwards from its own connector.
 */
function AllocationSliceLabel({ x, y, textAnchor, payload }) {
  if (!payload) return null
  return (
    <text x={x} y={y} textAnchor={textAnchor} dominantBaseline="central" fontSize={14}>
      <tspan fill="var(--text-primary)" fontWeight="600">
        {payload.percent.toFixed(1)}%
      </tspan>
      <tspan fill="var(--text-secondary)"> ({formatCurrency(payload.value, 0)})</tspan>
    </text>
  )
}

function ColorSwatch({ index }) {
  return (
    <span
      className="inline-block h-3.5 w-3.5 shrink-0 rounded-full"
      style={{ backgroundColor: chartColorAt(index) }}
    />
  )
}

function AllocationPieChart({ allocation }) {
  const [showTable, setShowTable] = useState(false)
  const slices = useMemo(() => toSlices(allocation), [allocation])

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
          {/* Roomier than the slices alone need: the labels and their leader lines sit outside
              the pie, so the radius stays small enough to keep them inside the card. */}
          <ResponsiveContainer width="100%" height={260}>
            <PieChart margin={{ top: 10, right: 10, bottom: 10, left: 10 }}>
              <Pie
                data={slices}
                cx="50%"
                cy="50%"
                outerRadius={52}
                dataKey="value"
                label={<AllocationSliceLabel />}
              >
                {slices.map((slice, index) => (
                  <Cell key={slice.assetType} fill={chartColorAt(index)} />
                ))}
              </Pie>
              <Tooltip content={<AllocationTooltip />} />
            </PieChart>
          </ResponsiveContainer>

          <div className="mt-2 flex flex-wrap gap-3">
            {slices.map((slice, index) => (
              <div key={slice.assetType} className="flex items-center gap-2 text-base">
                <ColorSwatch index={index} />
                <span className="text-[var(--text-secondary)]">{slice.name}</span>
              </div>
            ))}
          </div>
        </>
      )}
    </Card>
  )
}

export default AllocationPieChart
