// Fixtures for VITE_USE_MOCKS=true. Field names and semantics mirror the backend DTOs -
// in particular `costBasis` is the TOTAL amount paid for the position, not a per-share price.

import { isCashItem } from '../utils/portfolio';

/** Fixed "now" so the generated history and range filters stay deterministic. */
export const MOCK_TODAY = new Date('2026-07-28');

const mockHoldings = [
  {
    id: 'item-1',
    ticker: 'AAPL',
    assetType: 'stock',
    quantity: 50,
    costBasis: 7500,
    lastUpdated: MOCK_TODAY,
    currentPrice: 185.32,
    isFavourite: false,
  },
  {
    id: 'item-2',
    ticker: 'GOOG',
    assetType: 'stock',
    quantity: 30,
    costBasis: 3900,
    lastUpdated: MOCK_TODAY,
    currentPrice: 168.75,
    isFavourite: true,
  },
  {
    id: 'item-3',
    ticker: 'TSLA',
    assetType: 'stock',
    quantity: 15,
    costBasis: 4500,
    lastUpdated: MOCK_TODAY,
    currentPrice: 242.5,
    isFavourite: false,
  },
  {
    id: 'item-4',
    ticker: 'BND',
    assetType: 'bond',
    quantity: 100,
    costBasis: 10000,
    lastUpdated: MOCK_TODAY,
    currentPrice: 98.5,
    isFavourite: false,
  },
  {
    id: 'item-5',
    ticker: 'CASH',
    assetType: 'cash',
    quantity: 12340,
    costBasis: 12340,
    lastUpdated: MOCK_TODAY,
    currentPrice: 1,
    isFavourite: false,
  },
];

// Derive computed values, matching portfolioService.enrichItem. A non-cash holding with no
// currentPrice (unresolvable ticker) is valued at cost instead of $0, with gain/loss left
// unknown (null -> displayed as N/A).
export const enrichHoldings = (holdings) =>
  holdings.map((item) => {
    const isCash = isCashItem(item);

    if (!isCash && item.currentPrice == null) {
      return {
        ...item,
        currentPrice: null,
        marketValue: item.costBasis,
        gainLoss: null,
        gainLossPercent: null,
      };
    }

    const marketValue = isCash ? item.quantity : item.quantity * item.currentPrice;
    const gainLoss = isCash ? 0 : marketValue - item.costBasis;

    return {
      ...item,
      marketValue,
      gainLoss,
      gainLossPercent: item.costBasis > 0 ? (gainLoss / item.costBasis) * 100 : 0,
    };
  });

// Synthetic daily portfolio value over the trailing year: gentle upward drift plus noise.
const generatePerformanceData = () => {
  const data = [];
  let value = 100000;

  for (let daysAgo = 365; daysAgo >= 0; daysAgo -= 1) {
    const date = new Date(MOCK_TODAY);
    date.setDate(date.getDate() - daysAgo);

    value = Math.max(80000, value + (Math.random() - 0.48) * 1000);

    data.push({
      date: date.toISOString().split('T')[0],
      totalValue: Math.round(value * 100) / 100,
    });
  }

  return data;
};

export const mockPerformanceData = generatePerformanceData();

const mockTransactions = [
  { id: 'txn-1', portfolioItemId: 'item-1', type: 'buy', quantity: 50, price: 150, date: new Date('2026-01-15'), useCash: true },
  { id: 'txn-2', portfolioItemId: 'item-2', type: 'buy', quantity: 30, price: 130, date: new Date('2026-02-10'), useCash: true },
  { id: 'txn-3', portfolioItemId: 'item-3', type: 'buy', quantity: 15, price: 300, date: new Date('2026-03-05'), useCash: true },
  { id: 'txn-4', portfolioItemId: 'item-4', type: 'buy', quantity: 100, price: 100, date: new Date('2026-01-20'), useCash: true },
];

export const mockPortfolioData = {
  items: enrichHoldings(mockHoldings),
  transactions: mockTransactions,
};
