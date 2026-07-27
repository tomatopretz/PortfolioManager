# PORTFOLIO MANAGER - MINIMAL IMPLEMENTATION PLAN

## 1. MINIMAL DATA MODEL

### Core Portfolio Item Entity (Current Holdings)
```
PortfolioItem {
  id: string (UUID/auto-generated)
  ticker: string (e.g., "AAPL", "GOOG")
  quantity: number (current quantity held)
  costBasis: number (total cost of shares held - updated on transactions)
  currentPrice: number (cached from external source)
  lastUpdated: timestamp
}
```

### Transaction History Entity
```
Transaction {
  id: string (UUID/auto-generated)
  ticker: string (e.g., "AAPL", "GOOG")
  type: string ('buy' | 'sell')
  quantity: number (positive for both buy and sell)
  price: number (price per share)
  date: timestamp (transaction date)
  createdAt: timestamp (when added to system)
}
```

### Database Collection Structure (Firestore)
- Collection: `portfolio` (single document for current holdings)
  - Subcollection: `items` (current portfolio items)
- Collection: `transactions` (immutable transaction history)

---

## 2. CORE API ENDPOINTS

### Portfolio Operations
- `GET /api/portfolio` - Retrieve full portfolio (current holdings)
- `GET /api/portfolio/items` - List all items (paginated if needed)
- `GET /api/portfolio/performance` - Calculate portfolio metrics

### Transaction Management
- `POST /api/transactions` - Record a buy/sell transaction (updates portfolio items)
- `GET /api/transactions` - List all transactions (paginated, optionally filtered by ticker)
- `GET /api/transactions/{ticker}` - Get transaction history for specific ticker
- `DELETE /api/transactions/{transactionId}` - Remove transaction and update portfolio item

### Price Data
- `GET /api/prices/{ticker}` - Get current price for ticker
- `POST /api/prices/refresh` - Refresh all prices from Yahoo Finance

---

## 3. FRONTEND COMPONENT STRUCTURE

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

---

## 4. PROJECT STRUCTURE & SETUP

### Backend (Python)
```
backend/
├── app.py (Flask/FastAPI main)
├── requirements.txt
├── .env (Firebase credentials, API keys)
├── .gitignore
├── config.py (configuration)
├── firebase_config.py (Firestore setup)
├── models/
│   ├── portfolio.py
│   └── item.py
├── routes/
│   ├── portfolio.py
│   └── prices.py
├── services/
│   ├── firestore_service.py
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

### Phase 1: Backend API Foundation (Days 1-2)
1. Initialize Python project with Flask/FastAPI
2. Set up Firebase/Firestore connection
3. Implement `PortfolioItem` and `Transaction` models
4. Create Firestore service layer with CRUD operations
5. Implement endpoints: `GET /api/portfolio`, `GET /api/portfolio/items`
6. Add basic error handling and logging
7. **Deliverable:** Working API that retrieves empty portfolio

### Phase 2: Transactions (Days 2-3)
1. Implement `POST /api/transactions` endpoint (buy/sell)
2. Implement transaction logic to update `PortfolioItem` quantity and cost basis
3. Implement `GET /api/transactions` and `GET /api/transactions/{ticker}` endpoints
4. Add input validation (ticker format, quantity > 0, type validation)
5. Add error handling for invalid transactions (selling more than held)
6. **Deliverable:** Can record transactions via API and portfolio items update accordingly

### Phase 3: Price Integration (Days 3-4)
1. Integrate yfinance library for price fetching
2. Implement `GET /api/prices/{ticker}` endpoint
3. Add caching to avoid excessive Yahoo Finance calls
4. Implement `POST /api/prices/refresh` for batch updates
5. **Deliverable:** API returns current prices for holdings

### Phase 4: Frontend - Browse & Display (Days 4-5)
1. Create React app structure with routing
2. Implement `usePortfolio` hook for state management
3. Build `PortfolioContainer` and `PortfolioList` components
4. Implement `ItemTable` and `ItemRow` components
5. Connect to backend API endpoints
6. Add loading states and error handling
7. **Deliverable:** Browse page shows portfolio items with prices

### Phase 5: Frontend - Add/Remove UI (Day 5)
1. Build `ItemForm` modal component
2. Implement form validation matching backend
3. Connect to POST/DELETE endpoints
4. Add success/error toast notifications
5. Refresh list after operations
6. **Deliverable:** Full CRUD UI functional

### Phase 6: Performance Visualization (Days 6-7)
1. Calculate portfolio metrics (total value, gain/loss)
2. Build `PerformanceChart` with Recharts library
3. Implement `PerformanceMetrics` card display
4. Add `GET /api/portfolio/performance` endpoint
5. **Deliverable:** Performance page with charts and stats

### Phase 7: Polish & Deployment (Days 7-8)
1. Code cleanup and refactoring
2. Comprehensive testing (unit + integration)
3. Documentation (API docs, setup guide)
4. Deploy backend (Cloud Run, Heroku, or similar)
5. Deploy frontend (Vercel, Netlify, or similar)
6. **Deliverable:** Live application

---

## 6. DEPENDENCIES & SETUP REQUIREMENTS

### Backend Dependencies (Python)
- Flask or FastAPI (HTTP framework)
- firebase-admin (Firestore SDK)
- yfinance (Yahoo Finance data)
- python-dotenv (environment management)
- pydantic (data validation)
- requests (HTTP client)
- pytest (testing)
- CORS middleware (for frontend communication)

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
- Firebase project with Firestore database
- Google Cloud credentials JSON file
- Yahoo Finance API access (free, no key needed)

---

## 7. LOCAL DEVELOPMENT & DEPLOYMENT APPROACH

### Local Development
1. Create separate `.env.local` files for backend and frontend
2. Backend runs on `http://localhost:5000` (Flask default)
3. Frontend runs on `http://localhost:3000` (React default)
4. Firestore emulator can be used for offline testing
5. Use `docker-compose.yml` to spin up full stack locally

### Deployment Strategy (MVP)
- **Backend:** Deploy to Cloud Run (Google Cloud) or Railway/Render for free tier
- **Frontend:** Deploy to Vercel or Netlify (automatic from git)
- **Database:** Use Firebase hosted Firestore (free tier available)
- **CI/CD:** GitHub Actions for automated tests and deploys

### Environment Configuration

**Backend (.env)**
```
FIREBASE_CREDENTIALS_JSON=<path or inline>
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
- Cache prices in Firestore with timestamps
- Batch price updates rather than individual requests
- Paginate portfolio if it grows large

### Testing Strategy
- Unit tests for services (Firestore, price fetching)
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
- `/backend/services/firestore_service.py` - Firestore CRUD operations layer
- `/backend/services/price_service.py` - Yahoo Finance integration
- `/frontend/src/hooks/usePortfolio.js` - Portfolio state management hook
- `/frontend/src/components/Portfolio/PortfolioContainer.jsx` - Main portfolio UI container
- `/backend/routes/portfolio.py` - Core API endpoint definitions
