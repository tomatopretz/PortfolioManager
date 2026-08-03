import { mockPortfolioData, mockPerformanceData, enrichHoldings } from './mockData';

let mockData = structuredClone(mockPortfolioData);

const simulateLatency = () => new Promise((resolve) => setTimeout(resolve, 300));

export const getPortfolioItems = async () => {
  await simulateLatency();
  return mockData.items;
};

export const getPerformance = async (range = 'all') => {
  await simulateLatency();

  const today = new Date('2026-07-28');
  let filtered = [...mockPerformanceData];

  switch (range) {
    case '1d':
      filtered = filtered.filter((d) => {
        const date = new Date(d.date);
        const daysAgo = Math.floor((today - date) / (1000 * 60 * 60 * 24));
        return daysAgo <= 1;
      });
      break;
    case '1w':
      filtered = filtered.filter((d) => {
        const date = new Date(d.date);
        const daysAgo = Math.floor((today - date) / (1000 * 60 * 60 * 24));
        return daysAgo <= 7;
      });
      break;
    case '1m':
      filtered = filtered.filter((d) => {
        const date = new Date(d.date);
        const daysAgo = Math.floor((today - date) / (1000 * 60 * 60 * 24));
        return daysAgo <= 30;
      });
      break;
    case '6m':
      filtered = filtered.filter((d) => {
        const date = new Date(d.date);
        const daysAgo = Math.floor((today - date) / (1000 * 60 * 60 * 24));
        return daysAgo <= 180;
      });
      break;
    case '1y':
      filtered = filtered.filter((d) => {
        const date = new Date(d.date);
        const daysAgo = Math.floor((today - date) / (1000 * 60 * 60 * 24));
        return daysAgo <= 365;
      });
      break;
    case 'all':
    default:
      break;
  }

  return filtered;
};

export const getCurrentPrices = async (tickers) => {
  await simulateLatency();

  const prices = {};
  if (tickers && Array.isArray(tickers)) {
    tickers.forEach((ticker) => {
      const item = mockData.items.find((i) => i.ticker === ticker);
      if (item) {
        prices[ticker] = item.currentPrice;
      }
    });
  }
  return prices;
};

export const buyAsset = async (payload) => {
  await simulateLatency();

  const { ticker, assetType, quantity, price, useCash } = payload;

  if (useCash) {
    const cashItem = mockData.items.find((i) => i.ticker === 'CASH');
    const cost = quantity * price;
    if (cashItem && cashItem.quantity < cost) {
      throw new Error('Insufficient cash balance');
    }
    if (cashItem) {
      cashItem.quantity -= cost;
    }
  }

  let item = mockData.items.find(
    (i) => i.ticker === ticker && i.assetType === assetType
  );

  if (!item) {
    item = {
      id: `item-${Date.now()}`,
      ticker,
      assetType,
      quantity: 0,
      costBasis: 0,
      currentPrice: price,
      lastUpdated: new Date(),
    };
    mockData.items.push(item);
  }

  const cost = quantity * price;
  item.quantity += quantity;
  item.costBasis += cost;
  item.currentPrice = price;

  mockData.items = enrichHoldings(mockData.items);

  const transaction = {
    id: `txn-${Date.now()}`,
    portfolioItemId: item.id,
    type: 'buy',
    quantity,
    price,
    date: new Date(),
    useCash,
  };
  mockData.transactions.push(transaction);

  return { success: true, transaction };
};

export const sellAsset = async (payload) => {
  await simulateLatency();

  const { ticker, quantity, price } = payload;

  const item = mockData.items.find((i) => i.ticker === ticker);
  if (!item) {
    throw new Error(`Item not found: ${ticker}`);
  }
  if (item.quantity < quantity) {
    throw new Error(`Insufficient quantity to sell. Held: ${item.quantity}`);
  }

  const proceeds = quantity * price;
  const cashItem = mockData.items.find((i) => i.ticker === 'CASH');
  if (cashItem) {
    cashItem.quantity += proceeds;
  }

  const costPerShare = item.costBasis / item.quantity;
  item.quantity -= quantity;
  item.costBasis -= costPerShare * quantity;

  if (item.quantity === 0) {
    mockData.items = mockData.items.filter((i) => i.id !== item.id);
  }

  mockData.items = enrichHoldings(mockData.items);

  const transaction = {
    id: `txn-${Date.now()}`,
    portfolioItemId: item.id,
    type: 'sell',
    quantity,
    price,
    date: new Date(),
    useCash: true,
  };
  mockData.transactions.push(transaction);

  return { success: true, transaction };
};

export const getTransactions = async () => {
  await simulateLatency();
  return mockData.transactions;
};

export default {
  getPortfolioItems,
  getPerformance,
  getCurrentPrices,
  buyAsset,
  sellAsset,
  getTransactions,
};
