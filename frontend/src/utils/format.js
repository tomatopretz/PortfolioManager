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
  value == null ? 'N/A' : formatCurrency(value, fractionDigits)

export const formatSignedCurrencyOrNA = (value, fractionDigits = 2) => {
  if (value == null) return 'N/A'
  const formatted = formatCurrency(value, fractionDigits)
  return value >= 0 ? `+${formatted}` : formatted
}

export const formatSignedPercentOrNA = (value) => {
  if (value == null) return 'N/A'
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
}
