import { useState, useEffect, useRef, useCallback } from 'react'
import { getPortfolioItems, getPerformance, buyAsset, sellAsset, toggleFavourite } from '../services'

const MAX_FAVOURITES = 10

export const usePortfolio = () => {
  const [items, setItems] = useState([])
  const [performance, setPerformance] = useState([])
  const [itemsLoading, setItemsLoading] = useState(false)
  const [performanceLoading, setPerformanceLoading] = useState(false)
  const [error, setError] = useState(null)
  const [timeRange, setTimeRange] = useState('all')
  const itemsRequestId = useRef(0)
  const performanceRequestId = useRef(0)
  const loading = itemsLoading || performanceLoading

  const fetchItems = useCallback(async () => {
    const requestId = ++itemsRequestId.current
    setItemsLoading(true)
    setError(null)
    try {
      const data = await getPortfolioItems()
      if (requestId !== itemsRequestId.current) return
      setItems(data)
    } catch (err) {
      if (requestId !== itemsRequestId.current) return
      setError(err.message)
    } finally {
      if (requestId === itemsRequestId.current) {
        setItemsLoading(false)
      }
    }
  }, [])

  const fetchPerformance = useCallback(async (range = 'all') => {
    const requestId = ++performanceRequestId.current
    setPerformanceLoading(true)
    setError(null)
    try {
      const data = await getPerformance(range)
      if (requestId !== performanceRequestId.current) return
      setPerformance(data)
    } catch (err) {
      if (requestId !== performanceRequestId.current) return
      setError(err.message)
    } finally {
      if (requestId === performanceRequestId.current) {
        setPerformanceLoading(false)
      }
    }
  }, [])

  useEffect(() => {
    fetchItems()
  }, [fetchItems])

  useEffect(() => {
    fetchPerformance(timeRange)
  }, [fetchPerformance, timeRange])

  const handleBuy = async (payload) => {
    setError(null)
    try {
      await buyAsset(payload)
      await Promise.all([fetchItems(), fetchPerformance(timeRange)])
      return { success: true }
    } catch (err) {
      setError(err.message)
      return { success: false, error: err.message }
    }
  }

  const handleSell = async (payload) => {
    setError(null)
    try {
      await sellAsset(payload)
      await Promise.all([fetchItems(), fetchPerformance(timeRange)])
      return { success: true }
    } catch (err) {
      setError(err.message)
      return { success: false, error: err.message }
    }
  }

  const handleToggleFavourite = async (item) => {
    const isCash = String(item.assetType || '').toLowerCase() === 'cash'
    if (isCash) {
      return { success: false, error: 'CASH cannot be favourited' }
    }

    const isAddingFavourite = !item.isFavourite
    if (isAddingFavourite) {
      const favouriteCount = items.filter((i) => i.isFavourite).length
      if (favouriteCount >= MAX_FAVOURITES) {
        const message = `You can only favourite up to ${MAX_FAVOURITES} holdings.`
        setError(message)
        return { success: false, error: message }
      }
    }

    setError(null)
    setItems((current) =>
      current.map((i) => (i.id === item.id ? { ...i, isFavourite: !i.isFavourite } : i))
    )
    try {
      await toggleFavourite(item.ticker, item.assetType)
      return { success: true }
    } catch (err) {
      setItems((current) =>
        current.map((i) => (i.id === item.id ? { ...i, isFavourite: item.isFavourite } : i))
      )
      setError(err.message)
      return { success: false, error: err.message }
    }
  }

  const getTotalValue = () => {
    return items.reduce((sum, item) => sum + (item.marketValue || 0), 0)
  }

  const getCashBalance = () => {
    const cashItem = items.find((i) => {
      const ticker = String(i.ticker || '').toUpperCase()
      const assetType = String(i.assetType || '').toLowerCase()
      return ticker === 'CASH' || assetType === 'cash'
    })
    return cashItem ? Number(cashItem.marketValue ?? cashItem.quantity ?? 0) : 0
  }

  const getTotalCostBasis = () => {
    return items.reduce((sum, item) => sum + (item.costBasis || 0), 0) 
  }

  const getTotalReturn = () => {
    const totalValue = getTotalValue()
    const totalCostBasis = getTotalCostBasis()
    return {
      amount: totalValue - totalCostBasis,
      percent: totalCostBasis > 0 ? ((totalValue - totalCostBasis) / totalCostBasis) * 100 : 0,
    }
  }

  return {
    items,
    performance,
    loading: itemsLoading || performanceLoading,
    itemsLoading,
    performanceLoading,
    error,
    timeRange,
    setTimeRange,
    fetchItems,
    fetchPerformance,
    handleBuy,
    handleSell,
    handleToggleFavourite,
    getTotalValue,
    getCashBalance,
    getTotalCostBasis,
    getTotalReturn,
  }
}
