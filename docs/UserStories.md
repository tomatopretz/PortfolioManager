# User Stories — Portfolio Manager

| # | As a user, I want to... | So that... | Current flow | Page |
|---|---|---|---|---|
| 1 | See an overview of my portfolio when I open the app | I can quickly gauge how my investments are doing | [DashboardPage.jsx](../frontend/src/pages/DashboardPage.jsx): pie chart + performance chart + holdings preview + summary stats (empty state if no holdings). | Dashboard |
| 2 | See how my holdings are split across asset types | I can judge my diversification at a glance | [AllocationPieChart.jsx](../frontend/src/components/dashboard/AllocationPieChart.jsx), with a table-view toggle. | Dashboard |
| 3 | Switch between 1D/1W/1M/6M/1Y/All views of my portfolio value | I can compare short-term moves against long-term trends | [TimeRangeFilter.jsx](../frontend/src/components/dashboard/TimeRangeFilter.jsx) refetches `GET /api/performance` and updates [PerformanceChart.jsx](../frontend/src/components/dashboard/PerformanceChart.jsx). | Dashboard |
| 4 | See my top/favourite holdings right on the dashboard | I don't have to visit the full Holdings page for a quick check | [HoldingsPreview.jsx](../frontend/src/components/dashboard/HoldingsPreview.jsx): favourites first, then largest positions, max 10. | Dashboard |
| 5 | Buy a stock/bond or deposit cash into my portfolio | I can grow or fund my holdings | **Add Asset** button → [AddAssetModal.jsx](../frontend/src/components/portfolio/AddAssetModal.jsx) (fields vary by type) → `handleBuy` → `POST /api/transactions`. | Global (Header) |
| 6 | Sell a holding or withdraw cash | I can realize gains or access funds | **Delete Asset** button → [DeleteAssetModal.jsx](../frontend/src/components/portfolio/DeleteAssetModal.jsx) → `handleSell` → `POST /api/transactions`. | Global (Header) |
| 7 | Browse a full table of everything I hold | I can review my complete portfolio in one place | [HoldingsPage.jsx](../frontend/src/pages/HoldingsPage.jsx) + [HoldingsSummaryCards.jsx](../frontend/src/components/holdings/HoldingsSummaryCards.jsx). | Holdings |
| 8 | Search, filter by asset type, and sort my holdings | I can find a specific position quickly | Local search/filter/sort on `HoldingsPage`; zero-quantity rows sort last. | Holdings |
| 9 | Star/favourite up to 10 holdings | My most-watched positions are easy to spot | [FavouriteStar.jsx](../frontend/src/components/holdings/FavouriteStar.jsx) → `PATCH /api/portfolio/<ticker>/<asset_type>/favourite`, optimistic with rollback. | Holdings |
| 10 | See a log of every buy/sell/deposit/withdrawal | I can audit my past activity | [TransactionHistoryPage.jsx](../frontend/src/pages/TransactionHistoryPage.jsx): joins transactions with holdings, collapses auto-generated cash legs. | Transactions |
| 11 | Search, filter, and sort my transaction history | I can find a specific past trade | Local search/filter/sort on `TransactionHistoryPage` + [TransactionSummaryCards.jsx](../frontend/src/components/transactions/TransactionSummaryCards.jsx). | Transactions |

## Future / To Be Done (Scaling)

- Multi-currency cash support (currently CASH is tracked as a single USD balance).
- Multiple users & authentication (currently a single implicit portfolio, no login).
- Caching (e.g. prices/performance data) to reduce redundant upstream calls and speed up repeated requests.
