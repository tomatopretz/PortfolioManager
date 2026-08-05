import { useState } from 'react'
import Button from '../common/Button'
import Modal from '../common/Modal'
import { FormError } from '../common/FormControls'
import { Table, Tbody, Td, Th, Thead, Tr } from '../common/Table'
import { CASH_ASSET_TYPE } from '../../constants/portfolio'
import { formatCurrency, formatQuantity } from '../../utils/format'
import { parseTransactionsCsv } from '../../utils/transactionCsv'

const EMPTY_PARSE = { transactions: [], errors: [], skipped: [] }

function TransactionCsvImportModal({ isOpen, onClose, onImport }) {
  const [fileName, setFileName] = useState('')
  const [parseResult, setParseResult] = useState(EMPTY_PARSE)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const reset = () => {
    setFileName('')
    setParseResult(EMPTY_PARSE)
    setSubmitting(false)
    setError('')
  }

  const handleClose = () => {
    reset()
    onClose()
  }

  const handleFileChange = async (event) => {
    const [file] = event.target.files || []
    setError('')
    setParseResult(EMPTY_PARSE)
    setFileName(file?.name ?? '')
    if (!file) return

    try {
      const text = await file.text()
      setParseResult(parseTransactionsCsv(text))
    } catch {
      setError('Unable to read CSV file.')
    }
  }

  const handleImport = async () => {
    setSubmitting(true)
    setError('')

    try {
      await onImport(parseResult.transactions.map(({ rowNumber, ...transaction }) => transaction))
      handleClose()
    } catch (importError) {
      setError(importError.message)
    } finally {
      setSubmitting(false)
    }
  }

  const canImport =
    parseResult.transactions.length > 0 && parseResult.errors.length === 0 && !submitting

  const actionLabel = (transaction) => {
    if (transaction.assetType !== CASH_ASSET_TYPE.toUpperCase()) {
      return transaction.type.toUpperCase()
    }
    return transaction.type === 'buy' ? 'DEPOSIT' : 'WITHDRAWAL'
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      eyebrow="Transactions"
      title="Import CSV"
      closeLabel="Close import CSV modal"
    >
      <div className="space-y-5">
        <label className="block">
          <span className="mb-2 block text-sm font-semibold text-[var(--text-primary)]">
            CSV file
          </span>
          <input
            type="file"
            accept=".csv,text/csv"
            onChange={handleFileChange}
            className="block w-full rounded-lg border border-[var(--border)] bg-[var(--surface-1)] px-4 py-2 text-sm text-[var(--text-primary)] file:mr-4 file:rounded-md file:border-0 file:bg-[var(--surface-3)] file:px-3 file:py-1.5 file:text-sm file:font-semibold file:text-[var(--text-primary)] focus:border-[var(--primary)] focus:outline-none"
          />
        </label>

        {fileName && (
          <div className="rounded-lg border border-[var(--border)] bg-[var(--surface-1)] p-4">
            <div className="flex flex-wrap items-center justify-between gap-3 text-sm">
              <span className="font-semibold text-[var(--text-primary)]">{fileName}</span>
              <span className="text-[var(--text-secondary)]">
                {parseResult.transactions.length} ready
                {parseResult.skipped.length > 0 ? `, ${parseResult.skipped.length} skipped` : ''}
              </span>
            </div>
          </div>
        )}

        {parseResult.errors.length > 0 && (
          <div className="rounded-lg border border-[var(--status-serious)]/40 bg-[var(--status-serious)]/10 p-4 text-sm text-[var(--status-serious)]">
            {parseResult.errors.slice(0, 5).map((rowError) => (
              <p key={`${rowError.rowNumber}-${rowError.message}`}>
                Row {rowError.rowNumber}: {rowError.message}
              </p>
            ))}
            {parseResult.errors.length > 5 && <p>+{parseResult.errors.length - 5} more</p>}
          </div>
        )}

        {parseResult.transactions.length > 0 && (
          <div className="max-h-72 overflow-auto rounded-lg border border-[var(--border)]">
            <Table>
              <Thead sticky>
                <Th>Row</Th>
                <Th>Date</Th>
                <Th>Ticker</Th>
                <Th>Type</Th>
                <Th>Action</Th>
                <Th align="right">Quantity</Th>
                <Th align="right">Price</Th>
                <Th align="right">Use Cash</Th>
              </Thead>
              <Tbody>
                {parseResult.transactions.slice(0, 10).map((transaction) => (
                  <Tr key={transaction.rowNumber}>
                    <Td>{transaction.rowNumber}</Td>
                    <Td>{transaction.date}</Td>
                    <Td className="font-semibold text-[var(--text-primary)]">
                      {transaction.ticker}
                    </Td>
                    <Td>{transaction.assetType}</Td>
                    <Td>{actionLabel(transaction)}</Td>
                    <Td align="right">{formatQuantity(transaction.quantity)}</Td>
                    <Td align="right">{formatCurrency(transaction.price)}</Td>
                    <Td align="right">{transaction.useCash ? 'Yes' : 'No'}</Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </div>
        )}

        <FormError>{error}</FormError>

        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={handleClose}>
            Cancel
          </Button>
          <Button onClick={handleImport} disabled={!canImport}>
            {submitting ? 'Importing...' : 'Import CSV'}
          </Button>
        </div>
      </div>
    </Modal>
  )
}

export default TransactionCsvImportModal
