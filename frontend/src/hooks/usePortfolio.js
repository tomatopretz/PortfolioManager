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

  const itemsResource = useAsyncResource(getPortfolioItems, [])
  const performanceResource = useAsyncResource(getPerformance, [])

  const { data: items, setData: setItems, load: loadItems } = itemsResource
  const { data: performance, load: loadPerformance } = performanceResource

  useEffect(() => {
    loadItems()
  }, [loadItems])

  useEffect(() => {
    loadPerformance(timeRange)
  }, [loadPerformance, timeRange])

  // A trade changes both holdings and the value history, so refresh the two together.
  const refreshAll = useCallback(
    () => Promise.all([loadItems(), loadPerformance(timeRange)]),
    [loadItems, loadPerformance, timeRange]
  )

  const submitTransaction = useCallback(
    async (request, payload) => {
      setActionError(null)
      try {
        await request(payload)
        await refreshAll()
        setDataVersion((version) => version + 1)
        return { success: true }
      } catch (err) {
        setActionError(err.message)
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
        setItems((current) => current.map((i) => (i.id === item.id ? { ...i, isFavourite } : i)))

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
    [items, setItems]
  )

  const totals = useMemo(() => {
    const totalValue = sumBy(items, (item) => item.marketValue)
    const totalCostBasis = sumBy(items, (item) => item.costBasis)
    const cashItem = items.find(isCashItem)

    return {
      totalValue,
      totalCostBasis,
      cashBalance: cashItem ? Number(cashItem.marketValue ?? cashItem.quantity ?? 0) : 0,
      totalReturn: {
        amount: totalValue - totalCostBasis,
        percent: totalCostBasis > 0 ? ((totalValue - totalCostBasis) / totalCostBasis) * 100 : 0,
      },
    }
  }, [items])

  return {
    items,
    performance,
    itemsLoading: itemsResource.loading,
    performanceLoading: performanceResource.loading,
    loading: itemsResource.loading || performanceResource.loading,
    error: actionError ?? itemsResource.error ?? performanceResource.error,
    timeRange,
    setTimeRange,
    dataVersion,
    buyAsset,
    sellAsset,
    toggleFavourite,
    ...totals,
  }
}
