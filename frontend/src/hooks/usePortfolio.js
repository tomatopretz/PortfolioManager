import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  getPortfolioItems,
  getPerformance,
  buyAsset as requestBuy,
  sellAsset as requestSell,
  toggleFavourite as requestToggleFavourite,
} from '../services'
import { useAsyncResource } from './useAsyncResource'
import { DEFAULT_TIME_RANGE, MAX_FAVOURITES } from '../constants/portfolio'
import { isCashItem, sumBy } from '../utils/portfolio'

// Stable empty map so the initial render doesn't hand the chart a fresh object each time.
const NO_PERFORMANCE_RANGES = {}

// Stable empty portfolio so the initial render doesn't hand consumers a fresh object each time.
const EMPTY_PORTFOLIO = { items: [], totalValue: 0, totalCashBalance: 0, totalReturn: 0, totalReturnPercent: 0 }

/**
 * Owns all portfolio state. Intended to be instantiated exactly once, by `PortfolioProvider` —
 * components should read it through `usePortfolioContext` rather than calling this directly.
 */
export const usePortfolio = () => {
  const [timeRange, setTimeRange] = useState(DEFAULT_TIME_RANGE)
  const [actionError, setActionError] = useState(null)
  // Bumped after every successful trade. Views that own data this hook doesn't manage
  // (transaction history) depend on it to know their copy is stale.
  const [dataVersion, setDataVersion] = useState(0)

  const itemsResource = useAsyncResource(getPortfolioItems, EMPTY_PORTFOLIO)
  const performanceResource = useAsyncResource(getPerformance, NO_PERFORMANCE_RANGES)

  const { data: portfolio, setData: setPortfolio, load: loadItems, refresh: refreshItems } = itemsResource
  const { items } = portfolio
  const { data: performanceRanges, load: loadPerformance, refresh: refreshPerformance } = performanceResource

  useEffect(() => {
    loadItems()
  }, [loadItems])

  // The performance endpoint returns every range in a single response, so this runs once and
  // changing `timeRange` is a lookup below rather than a refetch - the chart never drops back
  // to a spinner just because a filter was clicked.
  useEffect(() => {
    loadPerformance()
  }, [loadPerformance])

  const performance = useMemo(
    () => performanceRanges[timeRange] ?? [],
    [performanceRanges, timeRange]
  )

  // Both a trade and a manual refresh invalidate holdings and the value history alike, so the
  // two are always re-fetched together. Deliberately `refresh` rather than `load`: the data is
  // already on screen, and blanking it back to a spinner on every price check reads as a page
  // reload rather than an update.
  const refreshAll = useCallback(
    () => Promise.all([refreshItems(), refreshPerformance(timeRange)]),
    [refreshItems, refreshPerformance, timeRange]
  )

  // Failures are returned to the caller only: the transaction modal owns the form and shows
  // them inline, so pushing them into `actionError` would also raise a banner on every page.
  const submitTransaction = useCallback(
    async (request, payload) => {
      setActionError(null)
      try {
        await request(payload)
        await refreshAll()
        setDataVersion((version) => version + 1)
        return { success: true }
      } catch (err) {
        return { success: false, error: err.message }
      }
    },
    [refreshAll]
  )

  const buyAsset = useCallback(
    (payload) => submitTransaction(requestBuy, payload),
    [submitTransaction]
  )

  const sellAsset = useCallback(
    (payload) => submitTransaction(requestSell, payload),
    [submitTransaction]
  )

  const toggleFavourite = useCallback(
    async (item) => {
      if (isCashItem(item)) {
        return { success: false, error: 'CASH cannot be favourited' }
      }

      if (!item.isFavourite && items.filter((i) => i.isFavourite).length >= MAX_FAVOURITES) {
        const message = `You can only favourite up to ${MAX_FAVOURITES} holdings.`
        setActionError(message)
        return { success: false, error: message }
      }

      setActionError(null)
      // Optimistic flip; rolled back to the item's original value if the request fails.
      const applyFavourite = (isFavourite) =>
        setPortfolio((current) => ({
          ...current,
          items: current.items.map((i) => (i.id === item.id ? { ...i, isFavourite } : i)),
        }))

      applyFavourite(!item.isFavourite)
      try {
        await requestToggleFavourite(item.ticker, item.assetType)
        return { success: true }
      } catch (err) {
        applyFavourite(item.isFavourite)
        setActionError(err.message)
        return { success: false, error: err.message }
      }
    },
    [items, setPortfolio]
  )

  // totalValue/totalCashBalance/totalReturn(Percent) now come from the backend (computed
  // alongside each item's pnl/gainLossPercent) rather than being summed/derived here.
  const totals = useMemo(
    () => ({
      totalValue: portfolio.totalValue,
      totalCostBasis: sumBy(items, (item) => item.costBasis),
      cashBalance: portfolio.totalCashBalance,
      totalReturn: {
        amount: portfolio.totalReturn,
        percent: portfolio.totalReturnPercent,
      },
    }),
    [items, portfolio]
  )

  return {
    items,
    performance,
    itemsLoading: itemsResource.loading,
    performanceLoading: performanceResource.loading,
    loading: itemsResource.loading || performanceResource.loading,
    refreshing: itemsResource.refreshing || performanceResource.refreshing,
    error: actionError ?? itemsResource.error ?? performanceResource.error,
    // Fetch errors only, excluding actionError: a failed trade shouldn't read as stale prices.
    refreshError: itemsResource.error ?? performanceResource.error,
    // Holdings carry the prices, so their fetch time is the one worth showing.
    pricesUpdatedAt: itemsResource.lastUpdatedAt,
    refreshAll,
    timeRange,
    setTimeRange,
    dataVersion,
    buyAsset,
    sellAsset,
    toggleFavourite,
    ...totals,
  }
}
