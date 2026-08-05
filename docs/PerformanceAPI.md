# Performance API & Frontend Components

## Performance API

### `GET /api/performance`

- **Route**: [routes/performance.py](../backend/routes/performance.py)
- **Service**: [services/performance_service.py](../backend/services/performance_service.py)

Returns chart-ready portfolio value history for six ranges in one response:

```json
{
  "ranges": {
    "1D": [{ "date": "2026-07-31T09:30:00Z", "value": 12345.67 }, ...],
    "1W": [{ "date": "2026-07-25", "value": 12000.0 }, ...],
    "1M": [...],
    "6M": [...],
    "1Y": [...],
    "ALL": [...]
  }
}
```

`1D` points are timestamped (intraday, `Z`-suffixed ISO datetimes); every other range is one point per calendar day (`YYYY-MM-DD`). On failure the route returns `502` with `{"error": "..."}`.

### How the history is built (`PerformanceService.get_performance`)

There's no stored time-series in the database — every point is reconstructed on the fly from two sources: the full transaction log and the *current* portfolio holdings. High-level flow:

1. **No transactions at all** → return one "now" point per range (or `[]` for every range if there are no holdings either), valuing today's holdings at the live market price (`price_service.list_current_prices`).
2. **Otherwise**, fetch daily close prices (`price_service.get_daily_price_history`) for every ticker ever touched, back to whichever is earlier: the first transaction, or 1 year ago (`ALL` can go further back than 1Y). Also fetch today's intraday 5-minute bars (`price_service.get_intraday_price_history`) for the `1D` range.
3. Build each of the 6 ranges from that shared price data.

**The key trick — reverse replay**: rather than replaying transactions forward from day one (error-prone, and the current DB state can drift from a perfect forward-replay due to rounding), the algorithm starts from `_current_holdings_snapshot()` — today's actual quantities, straight from the `portfolio_item` table — and walks *backwards* in time through the sorted transaction list, undoing each one (`_apply_transaction(..., reverse=True)`) as it passes each earlier date. This guarantees the *last* point in any range always matches today's real holdings exactly, and every earlier point reflects what the portfolio actually held at that moment.

- `_build_daily_range` walks day-by-day from `end_date` back to `start_date`, undoing any transaction dated after the current day, then values the resulting holdings via `_calculate_value` (holdings × the latest known close on/before that day — carrying forward the last available price on non-trading days).
- `_build_intraday_range` does the same but keyed on timestamps within the last 24 hours, mixing real 5-minute bars where the market was open with the last-known price held flat while it's closed — so a trade made pre-market still shows up even though there's no fresh intraday price for it yet (see the docstring on `_build_intraday_range` for the full reasoning, and the timezone note in `_to_naive_utc` — yfinance's intraday timestamps are exchange-local/aware, everything else is naive UTC, so they're normalized before comparison).
- CASH is tracked as a plain running dollar balance (no price lookup needed); it's recognized whether the ticker is `USD` or the assetType is `CASH` (`_normalize_cash_ticker`, `_is_cash_ticker`).

