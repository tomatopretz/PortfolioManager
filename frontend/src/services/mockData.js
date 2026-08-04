// Mock portfolio items and transaction data
// Mirrors the structure of backend/models/portfolio_item.py and backend/models/transaction.py

const mockHoldings = [
  {
    id: 'item-1',
    ticker: 'AAPL',
    assetType: 'stock',
    quantity: 50,
    costBasis: 130,
    lastUpdated: new Date('2026-07-28'),
    currentPrice: 185.32,
    isFavourite: false,
  },
  {
    id: 'item-2',
    ticker: 'GOOG',
    assetType: 'stock',
    quantity: 30,
    costBasis: 130,
    lastUpdated: new Date('2026-07-28'),
    currentPrice: 168.75,
    isFavourite: true,
  },
  {
    id: 'item-3',
    ticker: 'TSLA',
    assetType: 'stock',
    quantity: 15,
    costBasis: 300,
    lastUpdated: new Date('2026-07-28'),
    currentPrice: 242.50,
    isFavourite: false,
  },
  {
    id: 'item-4',
    ticker: 'BND',
    assetType: 'bond',
    quantity: 100,
    costBasis: 100,
    lastUpdated: new Date('2026-07-28'),
    currentPrice: 98.50,
    isFavourite: false,
  },
  {
    id: 'item-5',
    ticker: 'CASH',
    assetType: 'cash',
    quantity: 12340,
    costBasis: 1,
    lastUpdated: new Date('2026-07-28'),
    currentPrice: 1,
    isFavourite: false,
  },
];

// Derive computed values. A non-cash holding with no currentPrice (unresolvable ticker) is
// valued at cost instead of $0, with gain/loss left unknown (null -> displayed as N/A).
export const enrichHoldings = (holdings) => {
  return holdings.map((item) => {
    const isCash = item.assetType === 'cash';
    const priceUnavailable = !isCash && (item.currentPrice === null || item.currentPrice === undefined);

    if (priceUnavailable) {
      return {
        ...item,
        currentPrice: null,
        marketValue: item.costBasis * item.quantity,
        gainLoss: null,
        gainLossPercent: null,
      };
    }

    const marketValue = item.quantity * item.currentPrice;
    const gainLoss = marketValue - item.costBasis * item.quantity;
    const gainLossPercent = item.costBasis > 0 ? (gainLoss / item.costBasis * item.quantity) * 100 : 0;

    return {
      ...item,
      marketValue,
      gainLoss,
      gainLossPercent,
    };
  });
};

// Generate synthetic performance data (daily portfolio value over the last 1 year)
const generatePerformanceData = () => {
  const data = [];
  const today = new Date('2026-07-28');
  let value = 100000;

  for (let i = 365; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);

    // Simulate gentle upward trend with some volatility
    const randomChange = (Math.random() - 0.48) * 1000;
    value = Math.max(80000, value + randomChange);

    data.push({
      date: date.toISOString().split('T')[0],
      totalValue: Math.round(value * 100) / 100,
    });
  }

  return data;
};

export const mockPerformanceData = generatePerformanceData();

// Mock transactions
export const mockTransactions = [
  {
    id: 'txn-1',
    portfolioItemId: 'item-1',
    type: 'buy',
    quantity: 50,
    price: 150.0,
    date: new Date('2026-01-15'),
    useCash: true,
  },
  {
    id: 'txn-2',
    portfolioItemId: 'item-2',
    type: 'buy',
    quantity: 30,
    price: 130.0,
    date: new Date('2026-02-10'),
    useCash: true,
  },
  {
    id: 'txn-3',
    portfolioItemId: 'item-3',
    type: 'buy',
    quantity: 15,
    price: 300.0,
    date: new Date('2026-03-05'),
    useCash: true,
  },
  {
    id: 'txn-4',
    portfolioItemId: 'item-4',
    type: 'buy',
    quantity: 100,
    price: 100.0,
    date: new Date('2026-01-20'),
    useCash: true,
  },
];

export const mockPortfolioData = {
  items: enrichHoldings(mockHoldings),
  transactions: mockTransactions,
};
