// Intl's currency formatter puts the negative sign before the symbol (-$100.00), unlike naive
// `$${value}` string-building which produces the wrong $-100.00.
export const formatCurrency = (value, fractionDigits = 2) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  }).format(value ?? 0)
