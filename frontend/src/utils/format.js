// Intl's currency formatter puts the negative sign before the symbol (-$100.00), unlike naive
// `$${value}` string-building which produces the wrong $-100.00.
export const formatCurrency = (value) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value ?? 0)

export const formatCurrencyOrNA = (value) => (value == null ? 'N/A' : formatCurrency(value))

export const formatSignedCurrencyOrNA = (value) => {
  if (value == null) return 'N/A'
  const formatted = formatCurrency(value)
  return value >= 0 ? `+${formatted}` : formatted
}

export const formatSignedPercentOrNA = (value) => {
  if (value == null) return 'N/A'
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
}
