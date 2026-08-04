// Shared domain constants. Kept out of components so the UI, the hooks and the mock
// service all agree on the same set of asset types / time ranges.

export const CASH_ASSET_TYPE = 'cash'

export const ASSET_TYPE_OPTIONS = [
  { value: 'stock', label: 'Stock' },
  { value: 'bond', label: 'Bond' },
  { value: CASH_ASSET_TYPE, label: 'Cash' },
]

// `days` is the lookback window used to slice performance history; `null` means "everything".
export const TIME_RANGES = [
  { key: '1d', label: '1D', days: 1 },
  { key: '1w', label: '1W', days: 7 },
  { key: '1m', label: '1M', days: 30 },
  { key: '6m', label: '6M', days: 180 },
  { key: '1y', label: '1Y', days: 365 },
  { key: 'all', label: 'All', days: null },
]

export const DEFAULT_TIME_RANGE = 'all'

// The dashboard holdings table shows favourites first, then the largest remaining positions.
export const MAX_FAVOURITES = 10
export const MAX_PREVIEW_HOLDINGS = 10

// Categorical palette for the allocation chart. Index-based, wraps around.
const CHART_COLORS = [
  '#3b82f6',
  '#f97316',
  '#10b981',
  '#eab308',
  '#ec4899',
  '#22c55e',
  '#8b5cf6',
  '#ef4444',
]

export const chartColorAt = (index) => CHART_COLORS[index % CHART_COLORS.length]

export const PRIMARY_SERIES_COLOR = CHART_COLORS[0]
