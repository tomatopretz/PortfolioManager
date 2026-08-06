import { get, getBlob, patch, post } from './api';
import { TIME_RANGES } from '../constants/portfolio';
import { isCashItem, normalizeAssetType } from '../utils/portfolio';

// Backend returns costBasis/currentPrice/marketValue/pnl/gainLossPercent; the UI expects
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
  const gainLoss = isCash ? 0 : item.pnl ?? marketValue - item.costBasis;
  const gainLossPercent = isCash
    ? 0
    : item.gainLossPercent ?? (item.costBasis > 0 ? (gainLoss / item.costBasis) * 100 : 0);

  return { ...item, assetType, currentPrice, marketValue, gainLoss, gainLossPercent };
};

// Backend highlight shape is { ticker, marketValue, pnl, gainLossPercent }; rename pnl ->
// gainLoss to match enrichItem's field names. null passes through as-is (nothing to highlight).
const enrichHighlight = (highlight) =>
  highlight && { ...highlight, gainLoss: highlight.pnl };

// GET /api/portfolio now returns { items, totalValue, totalCashBalance, totalReturn,
// totalReturnPercent, allocationByType, largestPosition, topEarnerByAmount, topEarnerByPercent,
// worstEarnerByAmount, worstEarnerByPercent } - allocation and portfolio-wide extremes are
// computed backend-side alongside the totals instead of being derived client-side.
export const getPortfolioItems = async () => {
  const response = await get('/api/portfolio');
  return {
    items: (response?.items || []).map(enrichItem),
    totalValue: response?.totalValue ?? 0,
    totalCashBalance: response?.totalCashBalance ?? 0,
    totalReturn: response?.totalReturn ?? 0,
    totalReturnPercent: response?.totalReturnPercent ?? 0,
    allocation: response?.allocationByType ?? [],
    highlights: {
      largestPosition: enrichHighlight(response?.largestPosition),
      topEarnerByAmount: enrichHighlight(response?.topEarnerByAmount),
      topEarnerByPercent: enrichHighlight(response?.topEarnerByPercent),
      worstEarnerByAmount: enrichHighlight(response?.worstEarnerByAmount),
      worstEarnerByPercent: enrichHighlight(response?.worstEarnerByPercent),
    },
  };
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
