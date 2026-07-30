import { get, post } from './api';
// Backend returns costBasis/currentPrice/marketValue/unrealizedPnL; the dashboard components
// also expect gainLoss/gainLossPercent (as the mock service produces), so derive those here.
// CASH has no price concept on the backend (currentPrice/marketValue are null) - it's worth
// exactly its quantity in dollars, so it's priced at par instead of being dropped from totals.
const enrichItem = (item) => {
  const isCash = item.assetType === 'cash';
  const currentPrice = isCash ? 1 : item.currentPrice ?? 0;
  const marketValue = isCash ? item.quantity : item.marketValue ?? 0;
  const gainLoss = isCash ? 0 : item.unrealizedPnL ?? (marketValue - item.costBasis * item.quantity);
  const gainLossPercent = item.costBasis > 0 ? (gainLoss / (item.costBasis * item.quantity)) * 100 : 0;

  return {
    ...item,
    currentPrice,
    marketValue,
    gainLoss,
    gainLossPercent,
  };
};

export const getPortfolioItems = async () => {
  const response = await get('/api/portfolio');
  return (response || []).map(enrichItem);
};

export const getPerformance = async (range = 'all') => {
  const response = await get(`/api/portfolio/performance?range=${range}`);
  return response.data || [];
};

export const getCurrentPrices = async (tickers) => {
  if (!tickers || tickers.length === 0) {
    return {};
  }
  const tickerString = tickers.join(',');
  const response = await get(`/api/prices?tickers=${tickerString}`);
  return response.prices || {};
};

export const buyAsset = async (payload) => {
  const response = await post('/api/portfolio/add-asset', payload);
  return response;
};

export const sellAsset = async (payload) => {
  const response = await post('/api/portfolio/remove-asset', payload);
  return response;
};

export default {
  getPortfolioItems,
  getPerformance,
  getCurrentPrices,
  buyAsset,
  sellAsset,
};
