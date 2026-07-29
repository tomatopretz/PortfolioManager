import { get, post } from './api';

export const getPortfolioItems = async () => {
  const response = await get('/api/portfolio/items');
  return response.items || [];
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
