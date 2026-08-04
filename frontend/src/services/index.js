import * as realService from './portfolioService';
import * as mockService from './mockPortfolioService';

const useMocks = import.meta.env.VITE_USE_MOCKS === 'true' || import.meta.env.VITE_USE_MOCKS === true;

// Export the appropriate service implementation
const service = useMocks ? mockService : realService;

export const getPortfolioItems = service.getPortfolioItems;
export const getPerformance = service.getPerformance;
export const getCurrentPrices = service.getCurrentPrices;
export const buyAsset = service.buyAsset;
export const sellAsset = service.sellAsset;
export const getTransactions = service.getTransactions;
export const toggleFavourite = service.toggleFavourite;

export default service;
