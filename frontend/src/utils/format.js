const EM_DASH = '—'
const NOT_AVAILABLE = 'N/A'

// Intl's currency formatter puts the negative sign before the symbol (-$100.00), unlike naive
// `$${value}` string-building which produces the wrong $-100.00.
export const formatCurrency = (value, fractionDigits = 2) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  }).format(value ?? 0)

export const formatCurrencyOrNA = (value, fractionDigits = 2) =>
  value == null ? NOT_AVAILABLE : formatCurrency(value, fractionDigits)

const withSign = (value, formatted) => (value >= 0 ? `+${formatted}` : formatted)

export const formatSignedCurrencyOrNA = (value, fractionDigits = 2) =>
  value == null ? NOT_AVAILABLE : withSign(value, formatCurrency(value, fractionDigits))

export const formatPercent = (value, fractionDigits = 2) =>
  `${Number(value ?? 0).toFixed(fractionDigits)}%`

export const formatSignedPercentOrNA = (value, fractionDigits = 2) =>
  value == null ? NOT_AVAILABLE : withSign(value, formatPercent(value, fractionDigits))

export const formatQuantity = (value, maximumFractionDigits = 2) =>
  Number(value ?? 0).toLocaleString('en-US', { maximumFractionDigits })

// Compact axis label, e.g. 123456 -> "$123k".
export const formatCompactCurrency = (value) => `$${Math.round((value ?? 0) / 1000)}k`

export const formatDate = (value) => {
  if (!value) return EM_DASH
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return EM_DASH
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

export const capitalize = (value) => {
  const text = String(value ?? '')
  return text.charAt(0).toUpperCase() + text.slice(1)
}

export const pluralize = (count, singular, plural = `${singular}s`) =>
  `${count} ${count === 1 ? singular : plural}`

// Local (not UTC) YYYY-MM-DD, so a late-evening session doesn't default the date picker
// to tomorrow. Computed on call rather than at module load so long-lived tabs stay correct.
export const todayIso = () => {
  const now = new Date()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${now.getFullYear()}-${month}-${day}`
}
