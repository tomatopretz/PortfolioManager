import { useState, useEffect } from 'react'
import { getPortfolioItems, getPerformance, buyAsset, sellAsset } from '../services'

export const usePortfolio = () => {
  const [items, setItems] = useState([])
  const [performance, setPerformance] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [timeRange, setTimeRange] = useState('all')

  const fetchItems = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getPortfolioItems()
      setItems(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const fetchPerformance = async (range = 'all') => {
    setLoading(true)
    setError(null)
    try {
      const data = await getPerformance(range)
      setPerformance(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchItems()
    fetchPerformance(timeRange)
  }, [])

  useEffect(() => {
    fetchPerformance(timeRange)
  }, [timeRange])

  const handleBuy = async (payload) => {
    setLoading(true)
    setError(null)
    try {
      await buyAsset(payload)
      await fetchItems()
      return { success: true }
    } catch (err) {
      setError(err.message)
      return { success: false, error: err.message }
    } finally {
      setLoading(false)
    }
  }

  const handleSell = async (payload) => {
    setLoading(true)
    setError(null)
    try {
      await sellAsset(payload)
      await fetchItems()
      return { success: true }
    } catch (err) {
      setError(err.message)
      return { success: false, error: err.message }
    } finally {
      setLoading(false)
    }
  }

  const getTotalValue = () => {
    return items.reduce((sum, item) => sum + (item.marketValue || 0), 0)
  }

  const getCashBalance = () => {
    const cashItem = items.find((i) => i.ticker === 'CASH')
    return cashItem ? cashItem.quantity : 0
  }

  const getTotalCostBasis = () => {
    return items.reduce((sum, item) => sum + (item.costBasis * item.quantity || 0), 0) 
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
    loading,
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
