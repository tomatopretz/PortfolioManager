# PORTFOLIO MANAGER - MINIMAL IMPLEMENTATION PLAN

## 1. MINIMAL DATA MODEL

### Core Portfolio Item Entity (Current Holdings)
```
PortfolioItem {
  id: string (UUID/auto-generated)
  ticker: string (e.g., "AAPL", "GOOG", "CASH")
  assetType: string ('stock', 'bond', 'cash', etc)
  quantity: number (current quantity held)
  costBasis: number (total cost of current holdings)
  lastUpdated: timestamp
}
```

**Note:** `currentPrice` is fetched from Yahoo Finance at query time, not stored. 
**Special Case:** "CASH" is a PortfolioItem with quantity = available cash, costBasis = quantity

### Transaction History Entity
```
Transaction {
  id: string (UUID/auto-generated)
  portfolioItemId: string (which portfolio item was affected)
  type: string ('buy' | 'sell')
  quantity: number (positive for both buy and sell)
  price: number (price per share)
  date: timestamp (transaction date)
  useCash: boolean (true for sells, true/false for buys - indicates if cash was used)
}
```
**Note:** ticker and assetType are NOT stored; retrieved from related PortfolioItem

### Database Structure (Firebase SQL Connect / PostgreSQL)
- Table: `portfolio_item` (current portfolio items)
- Table: `transaction` (immutable transaction history)
- Relationship: `transaction.portfolio_item_id` references `portfolio_item.id`

---

## 2. CORE API ENDPOINTS & IMPLEMENTATION ARCHITECTURE

### Portfolio Operations
- `GET /api/portfolio` - Retrieve all portfolio items (current holdings and calculate market value and profit and loss (using cost basis and current price from yf))
- `GET /api/portfolio/{ticker}` - Get specific portfolio item by ticker
- `GET /api/portfolio/performance` - Calculate portfolio metrics
- `POST /api/portfolio` - Record a buy or sell (creates/updates PortfolioItem, adjusts CASH, records Transaction). The `type` field (`"buy"` | `"sell"`) in the request body picks the flow — see section 

### Transaction Management
- `GET /api/transactions` - List all transactions (paginated, optionally filtered via `?ticker=`)

### Price Data
- `GET /api/prices?tickers=AAPL,GOOG` - Get current prices for one or more tickers
- `GET /api/prices/{ticker}/{date}` - Get the price for one ticker on one specific date (YYYY-MM-DD)
- `POST /api/prices` - Refresh cached prices from Yahoo Finance

---

## 2A. BUSINESS LOGIC FOR BUY/SELL and ADD/REMOVE CASH - POST /api/portfolio

**Note:** All steps within ADD and REMOVE flows must be atomic—wrap in a database transaction so if any step fails, all changes rollback. There is no transaction-reversal endpoint; transactions are immutable once recorded.

### Request Parameters — POST /api/portfolio

| Field | Type | Stock/Bond (type="buy") | Stock/Bond (type="sell") | Cash (type="buy", Deposit) | Cash (type="sell", Withdraw) |
|---|---|---|---|---|---|
| type | string | required, `"buy"` | required, `"sell"` | required, `"buy"` | required, `"sell"` |
| ticker | string | required, e.g. "AAPL" | required, e.g. "AAPL" | required, fixed `"CASH"` | required, fixed `"CASH"` |
| assetType | string | required, e.g. "stock", "bond" | required, e.g. "stock", "bond" | required, fixed `"cash"` | required, fixed `"cash"` |
| quantity | number | required — shares to buy | required — shares to sell | required — cash amount to deposit | required — cash amount to withdraw |
| price | number | required — price per share | required — price per share | not sent / ignored (treated as 1) | not sent / ignored (treated as 1) |
| useCash | boolean | required — `true` deducts purchase amount from CASH, `false` skips cash check | not applicable — sells always credit proceeds to CASH (per the Transaction entity, sells always record `useCash=true`) | not sent / ignored (deposit never deducts CASH) | not applicable (withdrawing cash never credits itself) |

### ADD Flow (type="buy": Buy Stock/Bond OR Deposit Cash)
**Preconditions:**
- None (useCash determines cash handling for stock/bond; not applicable for cash deposit)

**Flow:**
1. Branch on `ticker`:
   - **If `ticker === "CASH"`** → go to step 2 (Cash Deposit)
   - **Else** → go to step 3 (Stock/Bond Buy)
2. **Cash Deposit path:**
   - Fetch the CASH PortfolioItem (create it if this is the first-ever deposit)
   - `cash.quantity += quantity`
   - `cash.costBasis += quantity` (cash costBasis is always 1:1 with quantity)
   - Create Transaction record: `type='buy'`, `portfolioItemId=CASH item id`, `quantity`, `price=1`, `useCash=false`
   - Update `lastUpdated` timestamp → **done**, skip steps 3-6
3. **Stock/Bond Buy path — if `useCash: true`:**
   - Fetch CASH item, verify balance ≥ purchase amount
   - Deduct from CASH: `cash.quantity -= (quantity × price)`
4. **If `useCash: false`:**
   - Skip cash balance check (user tracking existing holdings)
5. Check if PortfolioItem exists for ticker + assetType:
   - **If exists:** Update quantity and costBasis
     - `new quantity = existing quantity + bought quantity`
     - `new costBasis = existing costBasis + (bought quantity × price)`
   - **If not exists:** Create new PortfolioItem
6. Create Transaction record with type='buy', portfolioItemId, useCash=true/false
7. Update lastUpdated timestamps

### REMOVE Flow (Sell Stock/Bond OR Withdraw Cash)
**Preconditions:**
- Stock/bond: PortfolioItem exists with sufficient quantity
- Cash: CASH PortfolioItem balance ≥ withdrawal amount

**Flow:**
1. Branch on `ticker`:
   - **If `ticker === "CASH"`** → go to step 2 (Cash Withdrawal)
   - **Else** → go to step 3 (Stock/Bond Sell)
2. **Cash Withdrawal path:**
   - Fetch CASH PortfolioItem, verify `cash.quantity ≥ quantity` requested
   - `cash.quantity -= quantity`
   - `cash.costBasis -= quantity`
   - Create Transaction record: `type='sell'`, `portfolioItemId=CASH item id`, `quantity`, `price=1`, `useCash=false`
   - Update `lastUpdated` timestamp → **done**, skip steps 3-7
3. **Stock/Bond Sell path:** Fetch PortfolioItem to sell, verify quantity ≥ amount to sell
4. Calculate proceeds = `quantity sold × price per share`
5. Add to CASH: `cash.quantity += proceeds`
6. Update stock PortfolioItem:
   - Calculate `costBasis per share = existing costBasis / existing quantity`
   - `new costBasis = costBasis per share × new quantity`
   - `new quantity = existing quantity - sold quantity`
7. Create Transaction record with type='sell', portfolioItemId, useCash=true
8. If new quantity = 0, optionally delete PortfolioItem
9. Update lastUpdated timestamps

---


## 3. FRONTEND COMPONENT STRUCTURE

### Current Structure (✅ Implemented)
```
frontend/
├── index.html
├── package.json
├── vite.config.js (Vite + React plugin configured)
├── tailwind.config.js (custom color theme)
├── postcss.config.js (@tailwindcss/postcss configured)
├── .env.example (VITE_API_URL, VITE_USE_MOCKS)
├── src/
│   ├── main.jsx (React 18 entry point)
│   ├── App.jsx (Router setup)
│   ├── index.css (Tailwind + CSS custom properties for palette)
│   ├── theme/
│   │   └── colors.js (dataviz palette: categorical/sequential/status colors)
│   ├── services/ (✅ Complete)
│   │   ├── api.js (fetch wrapper, error handling)
│   │   ├── portfolioService.js (real API calls)
│   │   ├── mockPortfolioService.js (mock data with simulated latency)
│   │   ├── mockData.js (fixtures: holdings, transactions, performance series)
│   │   └── index.js (switchable service interface via VITE_USE_MOCKS)
│   ├── components/
│   │   ├── layout/ (✅ Complete)
│   │   │   ├── Header.jsx (logo, cash/total stats, Buy/Sell buttons)
│   │   │   ├── NavMenu.jsx (Dashboard | Holdings | Analytics with active styling)
│   │   │   └── AppLayout.jsx (Header + NavMenu + Outlet)
│   │   ├── dashboard/ (🚧 In progress)
│   │   │   ├── SummaryStats.jsx (KPI row: Total Value, Total Return, Cash Balance)
│   │   │   ├── AllocationPieChart.jsx (Asset-type breakdown, Recharts)
│   │   │   ├── PerformanceChart.jsx (Recharts AreaChart, single series)
│   │   │   ├── TimeRangeFilter.jsx (1W/1M/3M/YTD/1Y/All buttons)
│   │   │   └── HoldingsPreview.jsx (Top 5 holdings table preview)
│   │   ├── holdings/ (🔜 Planned)
│   │   │   ├── HoldingsTable.jsx (full table with sort/filter)
│   │   │   └── HoldingRow.jsx
│   │   ├── analytics/ (🔜 Planned)
│   │   │   ├── PerformanceChartFull.jsx
│   │   │   └── MetricsBreakdown.jsx (per-asset-type table)
│   │   ├── transactions/ (🔜 Planned)
│   │   │   ├── TransactionModal.jsx (Buy/Sell modal shell)
│   │   │   ├── BuyForm.jsx
│   │   │   └── SellForm.jsx
│   │   └── common/ (🔜 Planned)
│   │       ├── Modal.jsx (generic modal primitive)
│   │       ├── StatTile.jsx (value + delta per dataviz spec)
│   │       ├── ChartCard.jsx (figure wrapper with title, table-view toggle)
│   │       ├── Legend.jsx (categorical legend, toggle-to-isolate)
│   │       ├── Tooltip.jsx (shared tooltip: value bold, label secondary)
│   │       └── LoadingSpinner.jsx
│   ├── hooks/ (🔜 Planned)
│   │   └── usePortfolio.js (fetch + cache portfolio/performance, buy/sell mutators)
│   ├── context/ (🔜 Planned)
│   │   └── PortfolioContext.jsx (provides usePortfolio() app-wide)
│   └── pages/ (✅ Stubs created)
│       ├── DashboardPage.jsx (composes dashboard components)
│       ├── HoldingsPage.jsx (composes HoldingsTable)
│       └── AnalyticsPage.jsx (composes PerformanceChartFull + MetricsBreakdown)
└── tests/ (placeholder)
```

### Original Planned Structure (Reference)
```
src/
├── components/
│   ├── Portfolio/
│   │   ├── PortfolioContainer.jsx (main container)
│   │   ├── PortfolioSummary.jsx (overview/stats)
│   │   └── PortfolioList.jsx (list of items)
│   ├── Items/
│   │   ├── ItemForm.jsx (add/edit item modal)
│   │   ├── ItemRow.jsx (single item in table)
│   │   └── ItemTable.jsx (list container)
│   ├── Performance/
│   │   ├── PerformanceChart.jsx (graphical view)
│   │   └── PerformanceMetrics.jsx (key stats)
│   └── Common/
│       ├── Header.jsx
│       ├── Navigation.jsx
│       └── LoadingSpinner.jsx
├── services/
│   ├── api.js (axios instance + endpoint calls)
│   ├── portfolioService.js (business logic)
│   └── chartService.js (chart data helpers)
├── hooks/
│   ├── usePortfolio.js (main state management)
│   └── useFetch.js (generic fetch hook)
├── pages/
│   ├── BrowsePage.jsx (view items list)
│   ├── PerformancePage.jsx (charts & metrics)
│   └── EditPage.jsx (add/remove items)
├── App.jsx
└── index.js
```

**Note:** Current structure aligns with original plan. Uses Vite instead of Create React App (faster, more modern), and `fetch` instead of `axios` (fewer dependencies, same functionality).

---

## 4. PROJECT STRUCTURE & SETUP

### Backend (Python)
```
backend/
├── app.py (Flask/FastAPI main)
├── requirements.txt
├── .env (local backend configuration, API keys)
├── .gitignore
├── config.py (configuration)
├── db.py (PostgreSQL/SQL Connect setup)
├── models/
│   ├── portfolio.py
│   └── item.py
├── routes/
│   ├── portfolio.py
│   └── prices.py
├── services/
│   ├── db_service.py
│   ├── price_service.py (Yahoo Finance)
│   └── portfolio_service.py (business logic)
├── utils/
│   └── validators.py
└── tests/
    ├── test_api.py
    └── test_services.py
```

### Frontend (React)
```
frontend/
├── src/ (described above)
├── public/
├── package.json
├── .env (API base URL, Firebase config)
├── .gitignore
└── tests/
    └── components/
```

### Root Project
```
PortfolioManager/
├── backend/ (Python backend)
├── frontend/ (React frontend)
├── docker-compose.yml (optional for local dev)
├── .gitignore
├── README.md
└── docs/
    ├── API.md (endpoint documentation)
    ├── SETUP.md (local development guide)
    └── ARCHITECTURE.md (design decisions)
```

---

## 5. PRIORITIZED IMPLEMENTATION ROADMAP

### Phase 1: Backend Models & SQL Connect Setup (Days 1-2)
1. Initialize Python project with Flask
2.  Define `PortfolioItem` and `Transaction` Pydantic models
3. Set up Firebase SQL Connect/PostgreSQL connection
4. Create database service layer with CRUD operations
5. Implement endpoints: `GET /api/portfolio`, `GET /api/portfolio/items`
6. Add basic error handling and logging
7. **Deliverable:** Working API that retrieves empty portfolio

### Phase 2: Transactions (Days 2-3)
1. Implement `POST /api/portfolio/add-asset` and `POST /api/portfolio/remove-asset` endpoints (buy/sell)
2. Implement transaction logic to update `PortfolioItem` quantity and cost basis
3. Implement `GET /api/transactions` and `GET /api/transactions/{ticker}` endpoints
4. Add input validation (ticker format, quantity > 0, type validation)
5. Add error handling for invalid transactions (selling more than held)
6. **Deliverable:** Can record transactions via API and portfolio items update accordingly

### Phase 3: Price Integration (Days 3-4)
1. Integrate yfinance library for price fetching
2. Implement `GET /api/prices/tickers= {list of tickers} endpoint
3. Implement `GET /api/prices/{ticker}/{date}` endpoint
4. Add caching to avoid excessive Yahoo Finance calls
5. **Deliverable:** API returns current prices for holdings

### Phase 4: Frontend Setup & Layout (Days 4-5) — ✅ COMPLETED
1. ✅ Create React app with Vite (modern tooling, faster build/dev)
2. ✅ Install and configure React Router, Recharts, Tailwind CSS
3. ✅ Set up theme colors from dataviz palette (8-hue categorical, sequential blue, status colors)
4. ✅ Create service layer with mock data and switchable real/mock implementations
5. ✅ Build `AppLayout` with `Header` (logo, cash/total quick stats, Buy/Sell buttons) and `NavMenu`
6. ✅ Set up routing: Dashboard, Holdings, Analytics pages
7. ✅ Dev server running on port 3000 with HMR
8. ✅ **Deliverable:** Functional layout with navigation; ready for dashboard content

### Phase 5: Frontend Dashboard & Charts (Days 5-6) — 🔜 NEXT
1. Create `usePortfolio` hook for portfolio state management (fetch items, performance, buy/sell)
2. Implement `PortfolioContext` to share state across pages
3. Build dashboard components:
   - `SummaryStats`: KPI row with Total Value, Total Return ($ + %), Cash Balance (StatTile spec)
   - `AllocationPieChart`: Asset-type breakdown with categorical palette, legend, direct labels, tooltip, table-view toggle
   - `PerformanceChart`: Single-series area chart (portfolio value over time) with TimeRangeFilter (1W/1M/3M/YTD/1Y/All), crosshair+tooltip
   - `HoldingsPreview`: Top 5 holdings table with "View all" link to Holdings page
4. Wire chart interactions: time-range filter re-fetches/re-slices performance data
5. Validate pie and performance charts against dataviz palette (6-check validator)
6. **Deliverable:** Dashboard page fully functional with mock data

### Phase 6: Frontend Transaction UI & Holdings/Analytics Pages (Days 6-7)
1. Build transaction UI:
   - `Modal` primitive (overlay, focus trap, click-to-close, Esc key)
   - `BuyForm`: ticker, assetType, quantity, price, useCash checkbox with validation
   - `SellForm`: ticker select from holdings, quantity, price with max-held validation
   - Wire to Header buy/sell buttons with state management
2. Build Holdings page:
   - Full `HoldingsTable` with columns (ticker, assetType, qty, costBasis, price, marketValue, gainLoss $/%)
   - Client-side sort by column, text filter by ticker
   - Reuse `usePortfolio()` context (no refetch)
3. Build Analytics page:
   - Larger `PerformanceChartFull` (full-width, taller) with same time-range filter
   - `MetricsBreakdown`: per-asset-type table (costBasis vs. marketValue vs. return %)
4. **Deliverable:** Full CRUD UI + secondary pages functional with mock data

### Phase 7: Backend Endpoints Implementation (Days 7-8)
1. Implement `POST /api/portfolio/add-asset` (buy) with full transaction logic and Firestore atomicity
2. Implement `POST /api/portfolio/remove-asset` (sell) with validation and cash handling
3. Implement `GET /api/portfolio/performance` endpoint returning performance series by time range
4. Add input validation and error handling across all endpoints
5. Test endpoints with curl/Postman before frontend integration
6. **Deliverable:** All core API endpoints fully implemented

### Phase 8: Frontend-Backend Integration & Testing (Days 8-9)
1. Switch `services/index.js` from mock to real API (toggle `VITE_USE_MOCKS=false`)
2. Test buy/sell flows end-to-end (transaction creation, portfolio update, UI refresh)
3. Test time-range filtering on performance endpoint
4. Add loading states and error handling in UI
5. Test data consistency across pages and after refresh
6. **Deliverable:** Full app functional with real backend

### Phase 9: Polish, Testing & Deployment (Days 9-10)
1. Code cleanup and refactoring
2. Comprehensive testing (unit + integration)
3. Documentation (API docs, setup guide, frontend component docs)
4. Deploy backend (Cloud Run, Railway, or Render)
5. Deploy frontend (Vercel, Netlify)
6. Monitor for errors; iterate based on real-world usage
7. **Deliverable:** Live application

---

## 6. DEPENDENCIES & SETUP REQUIREMENTS

### Backend Dependencies (Python)
- Flask (HTTP framework)
- Flask-CORS (CORS middleware)
- psycopg (PostgreSQL driver)
- yfinance (Yahoo Finance data)
- python-dotenv (environment management)
- pydantic (data validation)
- requests (HTTP client)
- pytest (testing)
- gunicorn (production server)

### Frontend Dependencies
- react, react-dom
- react-router-dom (navigation)
- axios (HTTP client)
- recharts (charting library)
- tailwindcss or styled-components (styling)
- react-icons (UI icons)

### Local Development Requirements
- Python 3.9+
- Node.js 16+
- Firebase project with SQL Connect service
- Firebase CLI for SQL Connect local emulator and deployment
- Yahoo Finance API access (free, no key needed)

---

## 7. LOCAL DEVELOPMENT & DEPLOYMENT APPROACH

### Local Development
1. Create separate `.env.local` files for backend and frontend
2. Backend runs on `http://localhost:5000` (Flask default)
3. Frontend runs on `http://localhost:3000` (React default)
4. SQL Connect emulator can be used for offline testing
5. Use `docker-compose.yml` to spin up full stack locally
6. API docs (Swagger UI) are available at `http://localhost:5000/apidocs/swagger` while the backend is running (Redoc alternative at `/apidocs/redoc`, raw OpenAPI spec at `/apidocs/openapi.json`) — adjust the port if `API_PORT` is overridden

### Deployment Strategy (MVP)
- **Backend:** Deploy to Cloud Run (Google Cloud) or Railway/Render for free tier
- **Frontend:** Deploy to Vercel or Netlify (automatic from git)
- **Database:** Use Firebase SQL Connect backed by Cloud SQL PostgreSQL
- **CI/CD:** GitHub Actions for automated tests and deploys

### Environment Configuration

**Backend (.env)**
```
DATABASE_URL=<local or deployed PostgreSQL connection string>
FLASK_ENV=development|production
API_PORT=5000
CORS_ORIGIN=http://localhost:3000
```

**Frontend (.env)**
```
REACT_APP_API_URL=http://localhost:5000
REACT_APP_FIREBASE_CONFIG={...}
```

---

## 8. KEY IMPLEMENTATION CONSIDERATIONS

### Data Validation
- Backend: Validate ticker format (2-5 uppercase letters), volume > 0
- Frontend: Client-side validation + backend error handling

### Error Handling
- Graceful handling of invalid tickers from Yahoo Finance
- Network retry logic for price fetches
- User-friendly error messages in UI

### Performance Optimization
- Cache prices in PostgreSQL with timestamps
- Batch price updates rather than individual requests
- Paginate portfolio if it grows large

### Testing Strategy
- Unit tests for services (database, price fetching)
- Integration tests for API endpoints
- E2E tests for critical user flows (add/remove/view)

### Extensibility for Future Enhancements
- Structure allows easy addition of purchase price/date fields
- Performance metrics endpoint prepared for gain/loss calculations
- API design supports pagination and filtering
- Frontend components modular for future features (watchlists, alerts, etc.)

---

## Critical Files for Implementation

- `/backend/app.py` - Main Flask/FastAPI application entry point
- `/backend/services/db_service.py` - Database CRUD operations layer
- `/backend/services/price_service.py` - Yahoo Finance integration
- `/backend/routes/portfolio.py` - Core API endpoint definitions
- `/backend/routes/prices.py` - Price endpoints (implemented)
- `/backend/models/portfolio_item.py` - PortfolioItem Pydantic model
- `/backend/models/transaction.py` - Transaction Pydantic model

**Frontend:**
- `/frontend/src/hooks/usePortfolio.js` - Portfolio state management hook (next)
- `/frontend/src/context/PortfolioContext.jsx` - Global state provider (next)
- `/frontend/src/components/dashboard/AllocationPieChart.jsx` - Pie chart (next)
- `/frontend/src/components/dashboard/PerformanceChart.jsx` - Area chart (next)
- `/frontend/src/components/transactions/TransactionModal.jsx` - Buy/Sell modal (next)
- `/frontend/src/services/index.js` - Switchable service layer (done, ready for toggle)
