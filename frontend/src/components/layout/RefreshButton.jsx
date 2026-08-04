import { usePortfolioContext } from '../../context/PortfolioContext'
import Button from '../common/Button'
import { formatTime } from '../../utils/format'

// Circular-arrows glyph, in the same inline-SVG style as the sidebar icons.
const REFRESH_ICON =
  'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15'

// Deliberately unquantified: the lag is Yahoo's, it varies by exchange, and nothing in the
// response states it - so naming a specific number in the UI would be a guess presented as fact.
const DELAY_NOTE =
  "Prices come from Yahoo Finance's free feed, which lags the market. How far behind depends on the exchange."

/**
 * Re-fetches holdings and the value history on demand.
 *
 * Lives in the header so it reaches every page, and reports the time of the last successful
 * fetch — without it, a refresh that returns identical prices is indistinguishable from one
 * that silently did nothing.
 */
function RefreshButton() {
  const { refreshAll, refreshing, loading, refreshError, pricesUpdatedAt } = usePortfolioContext()

  return (
    <div className="flex items-center gap-3">
      <div className="text-right text-[11px] font-semibold leading-tight">
        {refreshError ? (
          <p className="text-[var(--status-serious)]" title={refreshError}>
            Refresh failed
          </p>
        ) : (
          <p className="text-[var(--text-secondary)]">Updated {formatTime(pricesUpdatedAt)}</p>
        )}
        <p className="text-[var(--text-muted)]" title={DELAY_NOTE}>
          Delayed quotes
        </p>
      </div>

      <Button
        variant="secondary"
        onClick={refreshAll}
        // Also disabled during the initial load, when there is nothing on screen to refresh yet.
        disabled={refreshing || loading}
        aria-label="Refresh prices"
      >
        <span className="flex items-center gap-2">
          <svg
            className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={REFRESH_ICON} />
          </svg>
          <span>{refreshing ? 'Refreshing' : 'Refresh'}</span>
        </span>
      </Button>
    </div>
  )
}

export default RefreshButton
