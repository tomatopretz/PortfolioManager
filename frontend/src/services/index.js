import * as realService from './portfolioService';
import * as mockService from './mockPortfolioService';

// Set VITE_USE_MOCKS=true to run the UI against in-memory fixtures with no backend.
const useMocks = String(import.meta.env.VITE_USE_MOCKS) === 'true';

const service = useMocks ? mockService : realService;

export const getPortfolioItems = service.getPortfolioItems;
export const getPerformance = service.getPerformance;
export const buyAsset = service.buyAsset;
export const sellAsset = service.sellAsset;
export const getTransactions = service.getTransactions;
export const toggleFavourite = service.toggleFavourite;
