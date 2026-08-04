import { mockPortfolioData, mockPerformanceData, enrichHoldings, MOCK_TODAY } from './mockData';
import { TIME_RANGES } from '../constants/portfolio';
import { isCashItem } from '../utils/portfolio';

const mockData = structuredClone(mockPortfolioData);

const simulateLatency = () => new Promise((resolve) => setTimeout(resolve, 300));

const DAY_MS = 1000 * 60 * 60 * 24;

const findItem = (ticker, assetType) =>
  mockData.items.find((item) => item.ticker === ticker && item.assetType === assetType);

const findCashItem = () => mockData.items.find(isCashItem);

const recordTransaction = (item, type, quantity, price, useCash) => {
  const transaction = {
    id: `txn-${Date.now()}`,
    portfolioItemId: item.id,
    type,
    quantity,
    price,
    date: new Date(),
    useCash,
  };
  mockData.transactions.push(transaction);
  return { success: true, transaction };
};

export const getPortfolioItems = async () => {
  await simulateLatency();
  return mockData.items;
};

export const getPerformance = async (range = 'all') => {
  await simulateLatency();

  const { days } = TIME_RANGES.find((entry) => entry.key === range) ?? {};
  if (!days) return [...mockPerformanceData];

  return mockPerformanceData.filter(
    (point) => Math.floor((MOCK_TODAY - new Date(point.date)) / DAY_MS) <= days
  );
};

export const buyAsset = async ({ ticker, assetType, quantity, price, useCash }) => {
  await simulateLatency();

  const cost = quantity * price;

  if (useCash) {
    const cashItem = findCashItem();
    if (cashItem) {
      if (cashItem.quantity < cost) throw new Error('Insufficient cash balance');
      cashItem.quantity -= cost;
    }
  }

  let item = findItem(ticker, assetType);
  if (!item) {
    item = {
      id: `item-${Date.now()}`,
      ticker,
      assetType,
      quantity: 0,
      costBasis: 0,
      currentPrice: price,
      lastUpdated: new Date(),
      isFavourite: false,
    };
    mockData.items.push(item);
  }

  item.quantity += quantity;
  item.costBasis += cost;
  item.currentPrice = price;

  mockData.items = enrichHoldings(mockData.items);

  return recordTransaction(item, 'buy', quantity, price, useCash);
};

export const sellAsset = async ({ ticker, assetType, quantity, price }) => {
  await simulateLatency();

  const item = findItem(ticker, assetType);
  if (!item) throw new Error(`Item not found: ${ticker}`);
  if (item.quantity < quantity) {
    throw new Error(`Insufficient quantity to sell. Held: ${item.quantity}`);
  }

  const cashItem = findCashItem();
  if (cashItem) cashItem.quantity += quantity * price;

  // Average-cost basis: selling removes the proportional share of the cost, not the proceeds.
  const costPerShare = item.costBasis / item.quantity;
  item.quantity -= quantity;
  item.costBasis -= costPerShare * quantity;

  if (item.quantity === 0) {
    mockData.items = mockData.items.filter((i) => i.id !== item.id);
  }

  mockData.items = enrichHoldings(mockData.items);

  return recordTransaction(item, 'sell', quantity, price, true);
};

export const getTransactions = async () => {
  await simulateLatency();
  return mockData.transactions;
};

export const toggleFavourite = async (ticker, assetType) => {
  await simulateLatency();

  const item = findItem(ticker, assetType);
  if (!item) throw new Error(`Item not found: ${ticker} (${assetType})`);
  if (isCashItem(item) && !item.isFavourite) throw new Error('CASH cannot be favourited');

  item.isFavourite = !item.isFavourite;
  mockData.items = enrichHoldings(mockData.items);

  return findItem(ticker, assetType);
};
