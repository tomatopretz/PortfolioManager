import { CASH_ASSET_TYPE } from '../constants/portfolio'

// Portfolio items arrive from two sources (live API + mock service) with slightly loose typing,
// so every predicate here defends against null/undefined instead of each call site doing it.

export const normalizeAssetType = (value) => String(value ?? '').toLowerCase()

export const isCashItem = (item) => normalizeAssetType(item?.assetType) === CASH_ASSET_TYPE

export const isZeroQuantity = (item) => Number(item?.quantity ?? 0) === 0

export const getMarketValue = (item) => Number(item?.marketValue ?? 0)

export const hasPrice = (item) => item?.currentPrice != null

/** Holdings that count towards allocation: priced, non-cash and actually held. */
export const isTradableHolding = (item) => !isCashItem(item) && getMarketValue(item) > 0

export const getCostBasisPerShare = (item) => {
  const quantity = Number(item?.quantity ?? 0)
  if (quantity === 0) return null
  return (item?.costBasis ?? 0) / quantity
}

export const sumBy = (items, selector) =>
  items.reduce((total, item) => total + (Number(selector(item)) || 0), 0)

/** Item with the highest (`max`) or lowest (`min`) value for `key`; null for an empty list. */
export const extremeBy = (items, key, mode = 'max') => {
  const isBetter = mode === 'max' ? (a, b) => a > b : (a, b) => a < b
  const fallback = mode === 'max' ? -Infinity : Infinity
  return items.reduce(
    (best, item) => (isBetter(item[key] ?? fallback, best?.[key] ?? fallback) ? item : best),
    null
  )
}

/** Tailwind text colour for a gain/loss figure: muted when unknown, green up, red down. */
export const toneClass = (value) => {
  if (value == null) return 'text-[var(--text-secondary)]'
  return value >= 0 ? 'text-[var(--status-good)]' : 'text-[var(--status-serious)]'
}
