import { Link } from 'react-router-dom'
import Card from '../common/Card'
import { Table, Tbody, Td, Th, Thead, Tr } from '../common/Table'
import { MAX_PREVIEW_HOLDINGS } from '../../constants/portfolio'
import {
  capitalize,
  formatCurrency,
  formatQuantity,
  formatSignedCurrencyOrNA,
  formatSignedPercentOrNA,
  pluralize,
} from '../../utils/format'
import { getMarketValue, hasPrice, isTradableHolding, toneClass } from '../../utils/portfolio'

/**
 * Favourites always lead, so a starred holding is guaranteed to be visible; the remaining
 * slots go to the largest positions by market value.
 */
const selectPreviewHoldings = (items) => {
  const eligible = items.filter(isTradableHolding)

  const favourites = eligible
    .filter((item) => item.isFavourite)
    .sort((a, b) => String(a.ticker).localeCompare(String(b.ticker)))

  const others = eligible
    .filter((item) => !item.isFavourite)
    .sort((a, b) => getMarketValue(b) - getMarketValue(a))
    .slice(0, Math.max(MAX_PREVIEW_HOLDINGS - favourites.length, 0))

  const holdings = [...favourites, ...others]
  return { holdings, remainingCount: eligible.length - holdings.length }
}

function HoldingsPreview({ items }) {
  const { holdings, remainingCount } = selectPreviewHoldings(items)

  if (holdings.length === 0) return null

  return (
    <Card padding="p-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-[var(--text-primary)]">Asset Holdings</h3>
          <p className="mt-1 text-xs text-[var(--text-secondary)]">
            Your favourites, plus top holdings by market value (max {MAX_PREVIEW_HOLDINGS})
          </p>
        </div>
        <Link
          to="/holdings"
          className="text-sm font-semibold text-[var(--primary)] transition-colors hover:text-[var(--primary-dark)]"
        >
          View all →
        </Link>
      </div>

      <Table>
        <Thead>
          <Th>Symbol</Th>
          <Th>Type</Th>
          <Th align="right">Shares</Th>
          <Th align="right">Current Price</Th>
          <Th align="right">Cost Basis</Th>
          <Th align="right">Market Value</Th>
          <Th align="right">P/L</Th>
        </Thead>
        <Tbody>
          {holdings.map((item) => {
            const priced = hasPrice(item)
            return (
              <Tr key={item.id}>
                <Td className="font-semibold text-[var(--text-primary)]">{item.ticker}</Td>
                <Td className="text-[var(--text-secondary)]">{capitalize(item.assetType)}</Td>
                <Td align="right" className="text-[var(--text-secondary)]">
                  {formatQuantity(item.quantity, 0)}
                </Td>
                <Td align="right" className="text-[var(--text-secondary)]">
                  {priced ? formatCurrency(item.currentPrice) : 'N/A'}
                </Td>
                <Td align="right" className="text-[var(--text-secondary)]">
                  {formatCurrency(item.costBasis)}
                </Td>
                <Td align="right" className="font-semibold text-[var(--text-primary)]">
                  {priced ? formatCurrency(item.marketValue) : 'N/A'}
                </Td>
                <Td align="right" className={`font-semibold ${toneClass(item.gainLoss)}`}>
                  {priced
                    ? `${formatSignedCurrencyOrNA(item.gainLoss)} (${formatSignedPercentOrNA(item.gainLossPercent)})`
                    : 'N/A'}
                </Td>
              </Tr>
            )
          })}
        </Tbody>
      </Table>

      {remainingCount > 0 && (
        <p className="mt-4 text-sm text-[var(--text-secondary)]">
          +{pluralize(remainingCount, 'more holding')} —{' '}
          <Link
            to="/holdings"
            className="font-semibold text-[var(--primary)] hover:text-[var(--primary-dark)]"
          >
            View all
          </Link>
        </p>
      )}
    </Card>
  )
}

export default HoldingsPreview
