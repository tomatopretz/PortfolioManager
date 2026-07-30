# Portfolio Manager - Frontend

A modern, responsive React-based frontend for the Portfolio Manager application. Built with Vite, TypeScript, React Router, and Tailwind CSS to provide a fast, scalable user interface for managing investment portfolios.

## Tech Stack

- **React 19** - UI library for building component-based interfaces
- **Vite 8** - Lightning-fast build tool and dev server
- **TypeScript** - Type-safe JavaScript for better development experience
- **React Router DOM 7** - Client-side routing and navigation
- **Tailwind CSS 4** - Utility-first CSS framework for styling
- **Recharts 3** - Composable React chart library for data visualization
- **PostCSS & Autoprefixer** - CSS processing and browser compatibility

## Setup

### Prerequisites

- Node.js 18+ and npm/yarn
- Git

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

## Running the Application

### Development Server

Start the Vite development server with hot module replacement (HMR):

```bash
npm run dev
```

The application will typically be available at `http://localhost:5173` and will automatically reload when you make changes.

### Production Build

Create an optimized production build:

```bash
npm run build
```

The built files will be in the `dist/` directory.

### Preview Production Build

Preview the production build locally:

```bash
npm run preview
```

## Project Structure

```
frontend/src/
├── components/
│   ├── common/              # Reusable UI components
│   │   ├── EmptyState.jsx
│   │   ├── LoadingSpinner.jsx
│   │   └── StatTile.jsx
│   ├── dashboard/           # Dashboard-specific components
│   │   ├── AllocationPieChart.jsx
│   │   ├── AssetBreakdown.jsx
│   │   ├── HoldingsPreview.jsx
│   │   ├── PerformanceChart.jsx
│   │   ├── SummaryStats.jsx
│   │   └── TimeRangeFilter.jsx
│   └── layout/              # Layout and navigation components
│       ├── AppLayout.jsx    # Main app wrapper with routes
│       ├── Header.jsx
│       ├── NavMenu.jsx
│       └── Sidebar.jsx
├── pages/                   # Page-level components (route components)
│   ├── DashboardPage.jsx    # Main dashboard view
│   ├── HoldingsPage.jsx     # Holdings list and details
│   └── PerformancePage.jsx  # Performance analytics
├── services/                # API and data services
│   ├── api.js              # API client configuration
│   ├── index.js            # Service exports and mock/real service selection
│   ├── portfolioService.js # Portfolio data service
│   ├── mockPortfolioService.js # Mock implementation for development
│   └── mockData.js         # Mock data and enrichment utilities
├── context/                 # React Context for state management
│   └── PortfolioContext.jsx # Global portfolio context
├── hooks/                   # Custom React hooks
│   └── usePortfolio.js     # Portfolio data hook
├── assets/                  # Static assets
├── App.jsx                 # Root app component with routing
├── main.jsx                # React DOM entry point
└── index.css               # Global styles and theme variables
```

## Architecture Overview

### Routing Structure

The application uses React Router with a nested layout pattern:

- **`/`** - Dashboard page (main landing)
- **`/holdings`** - Holdings management page
- **`/performance`** - Performance analytics page

All routes are wrapped in `AppLayout` which provides the header, sidebar, and navigation.

### State Management

- **PortfolioContext** - Global state for portfolio data
- **usePortfolio Hook** - Custom hook to consume portfolio context

### Component Hierarchy

```
App (routing + context provider)
└── Router
    └── AppLayout (header + sidebar + outlet)
        ├── DashboardPage
        │   ├── SummaryStats
        │   ├── AllocationPieChart
        │   ├── PerformanceChart
        │   └── ...
        ├── HoldingsPage
        └── PerformancePage
```

### Styling Approach

- **Tailwind CSS** - Utility-first styling with custom theme extensions in `tailwind.config.js`
- **CSS Custom Properties** - Color variables and theme configuration defined in `index.css` with light/dark mode support
- **Custom Animations** - Fade-in and fade-in-left animations defined in both `index.css` and `tailwind.config.js`
- **Responsive Design** - Mobile-first approach with Tailwind breakpoints
- **Dark Mode Support** - Automatic theme switching via CSS media queries
- **Icons** - Uses emoji icons for simple, universal symbol representation

## Data Services

### Portfolio Service

The `portfolioService.js` module handles all portfolio data fetching:

- Get portfolio summary
- Fetch holdings list
- Retrieve performance data
- Time-range filtering

### Mock Data

For development and testing, `mockPortfolioService.js` provides realistic mock data without requiring a backend connection.

## Development Tips

### Adding a New Component

1. Create the component in the appropriate `components/` subdirectory
2. Import and use it in a page or parent component
3. Use Tailwind classes for styling
4. Reference `StatTile.jsx` or `LoadingSpinner.jsx` for component patterns

### Adding a New Page

1. Create a new file in `pages/` (e.g., `NewPage.jsx`)
2. Add the route in `App.jsx`:
   ```jsx
   <Route path="/new-page" element={<NewPage />} />
   ```
3. Add navigation link in `Sidebar.jsx` or `Header.jsx`

### Using Charts

Charts are built with Recharts. Examples in `AllocationPieChart.jsx` and `PerformanceChart.jsx`.

### Accessing Portfolio Data

Use the `usePortfolio` hook in any component:

```jsx
import { usePortfolio } from '../hooks/usePortfolio'

function MyComponent() {
  const { portfolio, loading, error } = usePortfolio()
  // ...
}
```

## Build and Deployment

The frontend is optimized for production with:

- Code splitting
- Tree-shaking for unused code
- Minification and compression
- TypeScript type checking during build

To deploy, build the application and serve the `dist/` directory through a web server or hosting platform.

## TypeScript

The project uses TypeScript for type safety. Run type checking with:

```bash
npx tsc
```

This is also run automatically as part of `npm run build`.

## Performance Features

- **Vite's Fast HMR** - Near-instant updates during development
- **Lazy Loading** - Route-based code splitting with React Router
- **Optimized Rendering** - Component-level optimization with React 19
- **Tailwind CSS Purging** - Only includes used styles in production builds
