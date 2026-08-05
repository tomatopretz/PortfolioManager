import { Table, Tbody, Td, Th, Thead, Tr } from '../common/Table'
import FavouriteStar from './FavouriteStar'
import {
  capitalize,
  formatCurrency,
  formatCurrencyOrNA,
  formatDate,
  formatQuantity,
  formatSignedCurrencyOrNA,
  formatSignedPercentOrNA,
} from '../../utils/format'
import {
  getCostBasisPerShare,
  hasPrice,
  isCashItem,
  isZeroQuantity,
  toneClass,
} from '../../utils/portfolio'

const HOLDINGS_COLUMNS = [
  { key: 'ticker', label: 'Ticker' },
  { key: 'assetType', label: 'Type' },
  { key: 'quantity', label: 'Quantity', align: 'right' },
  { key: 'currentPrice', label: 'Current Price', align: 'right' },
  { key: 'costBasisPerShare', label: 'Cost Basis / Share', align: 'right' },
  { key: 'costBasis', label: 'Cost Basis', align: 'right' },
  { key: 'marketValue', label: 'Market Value', align: 'right' },
  { key: 'gainLoss', label: 'Gain/Loss ($)', align: 'right' },
  { key: 'gainLossPercent', label: 'Gain/Loss (%)', align: 'right' },
  { key: 'lastUpdated', label: 'Last Updated', align: 'right' },
]

function HoldingsTable({ rows, sort, onSort, onToggleFavourite }) {
  return (
    <Table scrollable>
      <Thead sticky>
        <Th>Fav</Th>
        {HOLDINGS_COLUMNS.map((column) => (
          <Th
            key={column.key}
            align={column.align}
            onClick={() => onSort(column.key)}
            sortDirection={sort.key === column.key ? sort.direction : undefined}
          >
            {column.label}
          </Th>
        ))}
      </Thead>
      <Tbody>
        {rows.map((item) => {
          const priced = hasPrice(item)
          const tone = toneClass(item.gainLoss)

          return (
            <Tr key={item.id}>
              <Td>
                <FavouriteStar
                  active={!!item.isFavourite}
                  disabled={isCashItem(item) || isZeroQuantity(item)}
                  disabledReason={
                    isCashItem(item)
                      ? 'Cash cannot be favourited'
                      : 'Positions you no longer hold cannot be favourited'
                  }
                  onToggle={() => onToggleFavourite(item)}
                />
              </Td>
              <Td className="font-semibold text-[var(--text-primary)]">{item.ticker}</Td>
              <Td className="text-[var(--text-secondary)]">{capitalize(item.assetType)}</Td>
              <Td align="right" className="text-[var(--text-secondary)]">
                {formatQuantity(item.quantity)}
              </Td>
              <Td align="right" className="text-[var(--text-secondary)]">
                {priced ? formatCurrency(item.currentPrice) : 'N/A'}
              </Td>
              <Td align="right" className="text-[var(--text-secondary)]">
                {formatCurrencyOrNA(getCostBasisPerShare(item))}
              </Td>
              <Td align="right" className="text-[var(--text-secondary)]">
                {formatCurrency(item.costBasis)}
              </Td>
              <Td align="right" className="font-semibold text-[var(--text-primary)]">
                {priced ? formatCurrency(item.marketValue) : 'N/A'}
              </Td>
              <Td align="right" className={`font-semibold ${tone}`}>
                {formatSignedCurrencyOrNA(item.gainLoss)}
              </Td>
              <Td align="right" className={`font-semibold ${tone}`}>
                {formatSignedPercentOrNA(item.gainLossPercent)}
              </Td>
              <Td align="right" className="text-[var(--text-secondary)]">
                {formatDate(item.lastUpdated)}
              </Td>
            </Tr>
          )
        })}
      </Tbody>
    </Table>
  )
}

export default HoldingsTable
