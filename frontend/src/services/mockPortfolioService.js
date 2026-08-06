import { mockPortfolioData, mockPerformanceData, enrichHoldings, MOCK_TODAY } from './mockData';
import { TIME_RANGES } from '../constants/portfolio';
import { isCashItem, normalizeAssetType } from '../utils/portfolio';

const mockData = structuredClone(mockPortfolioData);

const simulateLatency = () => new Promise((resolve) => setTimeout(resolve, 300));

const DAY_MS = 1000 * 60 * 60 * 24;

const findItem = (ticker, assetType) =>
  mockData.items.find((item) => item.ticker === ticker && item.assetType === assetType);

const findCashItem = () => mockData.items.find(isCashItem);

// Mirrors the real service's portfolio-wide totals, derived from the already-enriched items.
const computeTotals = (items) => {
  const cashItem = items.find(isCashItem);
  const totalCostBasis = items.reduce((sum, item) => sum + (item.costBasis ?? 0), 0);
  const totalReturn = items.reduce((sum, item) => sum + (item.gainLoss ?? 0), 0);
  return {
    totalValue: items.reduce((sum, item) => sum + (item.marketValue ?? 0), 0),
    totalCashBalance: cashItem ? Number(cashItem.marketValue ?? cashItem.quantity ?? 0) : 0,
    totalReturn,
    totalReturnPercent: totalCostBasis > 0 ? (totalReturn / totalCostBasis) * 100 : 0,
  };
};

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

// Mirrors the real service's allocation breakdown: priced holdings grouped by asset type
// (CASH as its own slice), largest first.
const computeAllocation = (items) => {
  const totalsByType = new Map();
  items.forEach((item) => {
    const marketValue = Number(item.marketValue ?? 0);
    if (marketValue <= 0) return;
    const key = isCashItem(item) ? 'cash' : normalizeAssetType(item.assetType) || 'other';
    totalsByType.set(key, (totalsByType.get(key) ?? 0) + marketValue);
  });

  const total = Array.from(totalsByType.values()).reduce((sum, value) => sum + value, 0);
  return Array.from(totalsByType, ([assetType, marketValue]) => ({
    assetType,
    marketValue: Math.round(marketValue * 100) / 100,
    percent: total > 0 ? Math.round((marketValue / total) * 100 * 100) / 100 : 0,
  })).sort((a, b) => b.marketValue - a.marketValue);
};

// Item with the highest (`max`) or lowest (`min`) value for `key`, ignoring items where it's
// null; null if none of `items` has a value at all.
const extremeBy = (items, key, mode = 'max') => {
  const isBetter = mode === 'max' ? (a, b) => a > b : (a, b) => a < b;
  let best = null;
  items.forEach((item) => {
    if (item[key] == null) return;
    if (best === null || isBetter(item[key], best[key])) best = item;
  });
  return best;
};

const toHighlight = (item) =>
  item && { ticker: item.ticker, marketValue: item.marketValue, gainLoss: item.gainLoss, gainLossPercent: item.gainLossPercent };

// Mirrors the real service's portfolio-wide extremes: largest position and top/worst earner
// by $ and %, among non-CASH holdings only.
const computeHighlights = (items) => {
  const nonCash = items.filter((item) => !isCashItem(item));
  return {
    largestPosition: toHighlight(extremeBy(nonCash, 'marketValue', 'max')),
    topEarnerByAmount: toHighlight(extremeBy(nonCash, 'gainLoss', 'max')),
    topEarnerByPercent: toHighlight(extremeBy(nonCash, 'gainLossPercent', 'max')),
    worstEarnerByAmount: toHighlight(extremeBy(nonCash, 'gainLoss', 'min')),
    worstEarnerByPercent: toHighlight(extremeBy(nonCash, 'gainLossPercent', 'min')),
  };
};

export const getPortfolioItems = async () => {
  await simulateLatency();
  return {
    items: mockData.items,
    ...computeTotals(mockData.items),
    allocation: computeAllocation(mockData.items),
    highlights: computeHighlights(mockData.items),
  };
};

// Mirrors the real service: every range in one call, keyed by `TIME_RANGES` key.
export const getPerformance = async () => {
  await simulateLatency();

  return Object.fromEntries(
    TIME_RANGES.map(({ key, days }) => [
      key,
      days
        ? mockPerformanceData.filter(
            (point) => Math.floor((MOCK_TODAY - new Date(point.date)) / DAY_MS) <= days
          )
        : [...mockPerformanceData],
    ])
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

export const bulkRecordTransactions = async (transactions) => {
  const created = [];

  for (const transaction of transactions) {
    const result =
      transaction.type === 'buy'
        ? await buyAsset(transaction)
        : await sellAsset(transaction);
    created.push(result.transaction);
  }

  return { count: created.length, created };
};

export const getTransactions = async () => {
  await simulateLatency();
  return mockData.transactions;
};

export const downloadTransactionsCsv = async () => {
  await simulateLatency();
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
