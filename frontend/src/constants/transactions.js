export const ALL_ACTIONS = 'all'

/**
 * A row's "action" is the user-facing verb, derived from the raw transaction `type` plus the
 * asset it touched: a buy of CASH reads as a deposit, a sell of CASH as a withdrawal.
 * `positive` drives the row colour - it means "added to the position or the cash balance".
 */
export const TRANSACTION_ACTIONS = {
  buy: { label: 'Buy', positive: true },
  sell: { label: 'Sell', positive: false },
  deposit: { label: 'Deposit', positive: true },
  withdrawal: { label: 'Withdrawal', positive: false },
}

export const ACTION_FILTER_OPTIONS = [
  { value: ALL_ACTIONS, label: 'All' },
  ...Object.entries(TRANSACTION_ACTIONS).map(([value, { label }]) => ({ value, label })),
]
