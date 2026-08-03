import { useState, useEffect, useRef } from 'react'
import { getPortfolioItems, getPerformance, buyAsset, sellAsset } from '../services'

export const usePortfolio = () => {
  const [items, setItems] = useState([])
  const [performance, setPerformance] = useState([])
  const [itemsLoading, setItemsLoading] = useState(false)
  const [performanceLoading, setPerformanceLoading] = useState(false)
  const [error, setError] = useState(null)
  const [timeRange, setTimeRange] = useState('all')
  const performanceRequestId = useRef(0)

  const fetchItems = async () => {
    setItemsLoading(true)
    setError(null)
    try {
      const data = await getPortfolioItems()
      setItems(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setItemsLoading(false)
    }
  }

  const fetchPerformance = async (range = 'all') => {
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
      if (requestId === performanceRequestId.current) setPerformanceLoading(false)
    }
  }

  useEffect(() => {
    fetchItems()
  }, [])

  useEffect(() => {
    fetchPerformance(timeRange)
  }, [timeRange])

  const handleBuy = async (payload) => {
    setItemsLoading(true)
    setError(null)
    try {
      await buyAsset(payload)
      await fetchItems()
      return { success: true }
    } catch (err) {
      setError(err.message)
      return { success: false, error: err.message }
    } finally {
      setItemsLoading(false)
    }
  }

  const handleSell = async (payload) => {
    setItemsLoading(true)
    setError(null)
    try {
      await sellAsset(payload)
      await fetchItems()
      return { success: true }
    } catch (err) {
      setError(err.message)
      return { success: false, error: err.message }
    } finally {
      setItemsLoading(false)
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
    getTotalValue,
    getCashBalance,
    getTotalCostBasis,
    getTotalReturn,
  }
}
