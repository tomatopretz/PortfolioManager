import { CASH_ASSET_TYPE } from '../constants/portfolio'
import { TRANSACTION_ACTIONS } from '../constants/transactions'
import { capitalize } from './format'
import { normalizeAssetType } from './portfolio'

const UNKNOWN_ASSET_TYPE = 'unknown'

/**
 * A buy/sell of a non-cash asset that used cash records a second, auto-generated CASH-item
 * Transaction row so the CASH balance stays in sync. The backend marks that companion row
 * useCash=true (it only exists because a trade caused it); a direct deposit/withdrawal against
 * CASH is always useCash=false. So a CASH-type row is a phantom leg to hide when useCash is
 * true, and a real deposit/withdrawal to keep (relabeled) when useCash is false.
 */
const isPhantomCashLeg = (row) => row.assetType === CASH_ASSET_TYPE && row.useCash

const toAction = (row) => {
  if (row.assetType !== CASH_ASSET_TYPE) return row.type
  return row.type === 'buy' ? 'deposit' : 'withdrawal'
}

/**
 * Joins raw transactions to the portfolio items they belong to (the API returns only
 * `portfolioItemId`, so ticker and asset type have to be looked up), derives the row total,
 * and drops the phantom cash legs.
 */
export const buildTransactionRows = (transactions, items) => {
  const itemsById = new Map(items.map((item) => [item.id, item]))

  return transactions
    .map((transaction) => {
      const item = itemsById.get(transaction.portfolioItemId)
      return {
        ...transaction,
        ticker: item?.ticker ?? 'Unknown',
        assetType: item ? normalizeAssetType(item.assetType) : UNKNOWN_ASSET_TYPE,
        total: Number(transaction.quantity ?? 0) * Number(transaction.price ?? 0),
      }
    })
    .filter((row) => !isPhantomCashLeg(row))
    .map((row) => ({ ...row, action: toAction(row) }))
}

export const compareTransactions = (a, b, key) => {
  if (key === 'date') {
    return new Date(a.date).getTime() - new Date(b.date).getTime()
  }

  const left = a[key]
  const right = b[key]

  if (typeof left === 'boolean' || typeof right === 'boolean') {
    return Number(left) - Number(right)
  }
  if (typeof left === 'string' || typeof right === 'string') {
    return String(left ?? '').localeCompare(String(right ?? ''))
  }
  return (left ?? 0) - (right ?? 0)
}

export const actionLabel = (action) => TRANSACTION_ACTIONS[action]?.label ?? capitalize(action)

export const actionToneClass = (action) =>
  TRANSACTION_ACTIONS[action]?.positive
    ? 'text-[var(--status-good)]'
    : 'text-[var(--status-serious)]'

/** `{ buy: 3, deposit: 1, ... }` in a single pass. */
export const countByAction = (rows) =>
  rows.reduce((counts, row) => {
    counts[row.action] = (counts[row.action] ?? 0) + 1
    return counts
  }, {})
