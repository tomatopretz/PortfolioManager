import { get, getBlob, patch, post } from './api';
import { TIME_RANGES } from '../constants/portfolio';
import { isCashItem, normalizeAssetType } from '../utils/portfolio';

// Backend returns costBasis/currentPrice/marketValue/unrealizedPnL; the UI also expects
// gainLoss/gainLossPercent (as the mock service produces), so derive those here.
//
// CASH has no price concept on the backend (currentPrice/marketValue are null) - it's worth
// exactly its quantity in dollars, so it's priced at par instead of being dropped from totals.
//
// A non-CASH ticker yfinance couldn't price arrives with currentPrice null. Rather than pricing
// it at $0 (which would understate the portfolio and read as "worthless"), value it at cost and
// leave gain/loss unknown - the UI shows N/A for price/market value/gain-loss on these rows.
const enrichItem = (item) => {
  const isCash = isCashItem(item);
  const assetType = normalizeAssetType(item.assetType) || item.assetType;

  if (!isCash && item.currentPrice == null) {
    return {
      ...item,
      assetType,
      currentPrice: null,
      marketValue: item.costBasis ?? 0,
      gainLoss: null,
      gainLossPercent: null,
    };
  }

  const currentPrice = isCash ? 1 : item.currentPrice ?? 0;
  const marketValue = isCash ? Number(item.quantity ?? 0) : item.marketValue ?? 0;
  const gainLoss = isCash ? 0 : item.unrealizedPnL ?? marketValue - item.costBasis;
  const gainLossPercent = item.costBasis > 0 ? (gainLoss / item.costBasis) * 100 : 0;

  return { ...item, assetType, currentPrice, marketValue, gainLoss, gainLossPercent };
};

export const getPortfolioItems = async () => {
  const response = await get('/api/portfolio');
  return (response || []).map(enrichItem);
};

const toChartPoints = (points) =>
  (points || []).map((point) => ({
    date: point.date,
    totalValue: Number(point.value ?? point.totalValue ?? 0),
  }));

// The endpoint returns every range in one payload, so this returns them all keyed by
// `TIME_RANGES` key. Switching the chart's range filter is then a lookup, not a request.
export const getPerformance = async () => {
  const response = await get('/api/performance');
  const ranges = response?.ranges || {};

  return Object.fromEntries(
    TIME_RANGES.map(({ key }) => [key, toChartPoints(ranges[key.toUpperCase()] ?? ranges[key])])
  );
};

const recordTransaction = (payload) => post('/api/transactions', payload);

export const buyAsset = recordTransaction;
export const sellAsset = recordTransaction;

export const bulkRecordTransactions = async (transactions) => {
  const response = await post('/api/transactions/bulk', { transactions });
  return response;
};

export const getTransactions = async () => {
  const response = await get('/api/transactions');
  return response || [];
};

export const downloadTransactionsCsv = async () => {
  const blob = await getBlob('/api/transactions/export');
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `transactions-${new Date().toISOString().slice(0, 10)}.csv`;
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
};

export const toggleFavourite = async (ticker, assetType) => {
  const response = await patch(
    `/api/portfolio/${encodeURIComponent(ticker)}/${encodeURIComponent(assetType)}/favourite`
  );
  return enrichItem(response);
};
