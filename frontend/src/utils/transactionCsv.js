export const TRANSACTION_CSV_HEADERS = ['Date', 'Ticker', 'Type', 'Action', 'Quantity', 'Price', 'UseCash']

const REQUIRED_HEADERS = TRANSACTION_CSV_HEADERS.map((header) => header.toLowerCase())

const normalizeHeader = (value) => String(value ?? '').trim().toLowerCase()

const parseCsvRows = (text) => {
  const rows = []
  let row = []
  let field = ''
  let inQuotes = false

  for (let index = 0; index < text.length; index += 1) {
    const char = text[index]
    const next = text[index + 1]

    if (char === '"') {
      if (inQuotes && next === '"') {
        field += '"'
        index += 1
      } else {
        inQuotes = !inQuotes
      }
    } else if (char === ',' && !inQuotes) {
      row.push(field)
      field = ''
    } else if ((char === '\n' || char === '\r') && !inQuotes) {
      if (char === '\r' && next === '\n') index += 1
      row.push(field)
      rows.push(row)
      row = []
      field = ''
    } else {
      field += char
    }
  }

  row.push(field)
  rows.push(row)

  return rows.filter((csvRow) => csvRow.some((cell) => String(cell).trim() !== ''))
}

const parseUseCash = (value) => {
  const normalized = String(value ?? '').trim().toLowerCase()
  if (['true', 'yes', 'y', '1'].includes(normalized)) return true
  if (['false', 'no', 'n', '0'].includes(normalized)) return false
  return null
}

export const parseTransactionsCsv = (text) => {
  const rows = parseCsvRows(text.replace(/^\uFEFF/, ''))
  const [headerRow, ...dataRows] = rows
  const errors = []
  const skipped = []
  const transactions = []

  if (!headerRow) {
    return { transactions, errors: [{ rowNumber: 1, message: 'CSV file is empty.' }], skipped }
  }

  const headerIndexes = new Map()
  headerRow.forEach((header, index) => {
    headerIndexes.set(normalizeHeader(header), index)
  })

  const missingHeaders = REQUIRED_HEADERS.filter((header) => !headerIndexes.has(header))
  if (missingHeaders.length > 0) {
    return {
      transactions,
      errors: [{ rowNumber: 1, message: `Missing columns: ${missingHeaders.join(', ')}` }],
      skipped,
    }
  }

  const cell = (row, header) => String(row[headerIndexes.get(header)] ?? '').trim()

  dataRows.forEach((row, index) => {
    const rowNumber = index + 2
    const date = cell(row, 'date')
    let ticker = cell(row, 'ticker').toUpperCase()
    let assetType = cell(row, 'type').toUpperCase()
    const action = cell(row, 'action').toLowerCase()
    const quantity = Number(cell(row, 'quantity'))
    const price = Number(cell(row, 'price'))
    const useCash = parseUseCash(cell(row, 'usecash'))
    const isCashAction = action === 'deposit' || action === 'withdrawal'
    const isCashRow = ticker === 'USD' || assetType === 'CASH' || isCashAction
    const backendType =
      action === 'deposit' ? 'buy' : action === 'withdrawal' ? 'sell' : action

    if (isCashRow) {
      ticker = 'USD'
      assetType = 'CASH'
    }

    if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
      errors.push({ rowNumber, message: 'Date must be YYYY-MM-DD.' })
    }
    if (!ticker) {
      errors.push({ rowNumber, message: 'Ticker is required.' })
    }
    if (!assetType) {
      errors.push({ rowNumber, message: 'Type is required.' })
    }
    if (!['buy', 'sell', 'deposit', 'withdrawal'].includes(action)) {
      errors.push({ rowNumber, message: 'Action must be BUY, SELL, DEPOSIT, or WITHDRAWAL.' })
    }
    if (!Number.isFinite(quantity) || quantity <= 0) {
      errors.push({ rowNumber, message: 'Quantity must be greater than zero.' })
    } else if (!isCashRow && !Number.isInteger(quantity)) {
      errors.push({ rowNumber, message: 'Quantity must be a whole number.' })
    }
    if (!isCashRow && (!Number.isFinite(price) || price <= 0)) {
      errors.push({ rowNumber, message: 'Price must be greater than zero.' })
    }
    if (useCash === null) {
      errors.push({ rowNumber, message: 'UseCash must be TRUE or FALSE.' })
    }

    if (errors.some((error) => error.rowNumber === rowNumber)) return

    transactions.push({
      rowNumber,
      date,
      ticker,
      assetType,
      type: backendType,
      quantity,
      price: isCashRow ? 1 : price,
      useCash: isCashRow ? false : useCash,
    })
  })

  return { transactions, errors, skipped }
}
