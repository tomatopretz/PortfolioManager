import { Table, Tbody, Td, Th, Thead, Tr } from '../common/Table'
import { capitalize, formatCurrency, formatDate, formatQuantity } from '../../utils/format'
import { actionLabel, actionToneClass } from '../../utils/transactions'

const TRANSACTION_COLUMNS = [
  { key: 'date', label: 'Date' },
  { key: 'ticker', label: 'Ticker' },
  { key: 'assetType', label: 'Type' },
  { key: 'action', label: 'Action' },
  { key: 'quantity', label: 'Quantity', align: 'right' },
  { key: 'price', label: 'Price', align: 'right' },
  { key: 'total', label: 'Total', align: 'right' },
  { key: 'useCash', label: 'Cash Used', align: 'right' },
]

function TransactionsTable({ rows, sort, onSort }) {
  return (
    <Table scrollable>
      <Thead sticky>
        {TRANSACTION_COLUMNS.map((column) => (
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
        {rows.map((row) => (
          <Tr key={row.id}>
            <Td className="text-[var(--text-secondary)]">{formatDate(row.date)}</Td>
            <Td className="font-semibold text-[var(--text-primary)]">{row.ticker}</Td>
            <Td className="text-[var(--text-secondary)]">{capitalize(row.assetType)}</Td>
            <Td className={`font-semibold ${actionToneClass(row.action)}`}>
              {actionLabel(row.action)}
            </Td>
            <Td align="right" className="text-[var(--text-secondary)]">
              {formatQuantity(row.quantity)}
            </Td>
            <Td align="right" className="text-[var(--text-secondary)]">
              {formatCurrency(row.price)}
            </Td>
            <Td align="right" className="font-semibold text-[var(--text-primary)]">
              {formatCurrency(row.total)}
            </Td>
            <Td align="right" className="text-[var(--text-secondary)]">
              {row.useCash ? 'Yes' : 'No'}
            </Td>
          </Tr>
        ))}
      </Tbody>
    </Table>
  )
}

export default TransactionsTable
