import { useState } from 'react'

const today = new Date().toISOString().slice(0, 10)

const defaultFormState = {
  ticker: '',
  assetType: 'stock',
  quantity: '',
  price: '',
  amount: '',
  date: today,
}

function DeleteAssetModal({ isOpen, onClose, onSubmit }) {
  const [formData, setFormData] = useState(defaultFormState)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const isCashAsset = formData.assetType === 'cash'

  const handleFieldChange = (event) => {
    const { name, value } = event.target
    setFormData((current) => ({
      ...current,
      [name]: value,
    }))
    setError('')
  }

  const resetForm = () => {
    setFormData(defaultFormState)
    setError('')
  }

  const handleClose = () => {
    resetForm()
    onClose()
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSubmitting(true)
    setError('')

    try {
      const payload = {
        type: 'sell',
        ticker: isCashAsset ? 'USD' : formData.ticker.trim().toUpperCase(),
        assetType: formData.assetType,
        quantity: Number(isCashAsset ? formData.amount : formData.quantity),
        price: isCashAsset ? 1 : Number(formData.price),
        date: formData.date,
      }

      if (isCashAsset) {
        if (!payload.quantity || payload.quantity <= 0) {
          throw new Error('Please enter a valid withdrawal amount.')
        }
      } else {
        if (!payload.ticker) {
          throw new Error('Ticker is required.')
        }
        if (!payload.quantity || payload.quantity <= 0) {
          throw new Error('Quantity must be greater than zero.')
        }
        if (!payload.price || payload.price <= 0) {
          throw new Error('Price must be greater than zero.')
        }
      }

      if (!onSubmit) {
        throw new Error('Submit handler is not available.')
      }

      const result = await onSubmit(payload)
      if (!result?.success) {
        throw new Error(result?.error || 'Unable to sell this asset.')
      }

      handleClose()
    } catch (submitError) {
      setError(submitError.message)
    } finally {
      setSubmitting(false)
    }
  }

  if (!isOpen) {
    return null
  }

  const handleBackdropClick = (event) => {
    if (event.target === event.currentTarget) {
      handleClose()
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4 backdrop-blur-sm"
      onClick={handleBackdropClick}
    >
      <div className="w-full max-w-xl rounded-2xl border border-[var(--border)] bg-[var(--surface-1)] p-6 shadow-[var(--shadow-lg)]">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[var(--text-secondary)]">
              New Transaction
            </p>
            <h2 className="mt-1 text-2xl font-bold text-[var(--text-primary)]">Sell Asset</h2>
          </div>

          <button
            type="button"
            onClick={handleClose}
            className="rounded-full border border-[var(--border)] bg-[var(--surface-2)] p-2 text-[var(--text-secondary)] hover:bg-[var(--surface-3)]"
            aria-label="Close sell asset form"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label htmlFor="assetType" className="mb-2 block text-sm font-medium text-[var(--text-primary)]">
              Asset Type
            </label>
            <select
              id="assetType"
              name="assetType"
              value={formData.assetType}
              onChange={handleFieldChange}
              className="w-full rounded-lg border border-[var(--gridline)] bg-[var(--surface-2)] px-3 py-2.5 text-[var(--text-primary)] outline-none ring-0 transition-colors focus:border-[var(--primary)]"
            >
              <option value="stock">Stock</option>
              <option value="bond">Bond</option>
              <option value="cash">Cash</option>
            </select>
          </div>

          {!isCashAsset && (
            <div>
              <label htmlFor="ticker" className="mb-2 block text-sm font-medium text-[var(--text-primary)]">
                Ticker
              </label>
              <input
                id="ticker"
                name="ticker"
                type="text"
                value={formData.ticker}
                onChange={handleFieldChange}
                placeholder="AAPL"
                className="w-full rounded-lg border border-[var(--gridline)] bg-[var(--surface-2)] px-3 py-2.5 text-[var(--text-primary)] placeholder:text-[var(--text-muted)] outline-none transition-colors focus:border-[var(--primary)]"
              />
            </div>
          )}

          {isCashAsset ? (
            <div>
              <label htmlFor="amount" className="mb-2 block text-sm font-medium text-[var(--text-primary)]">
                Withdrawal Amount
              </label>
              <input
                id="amount"
                name="amount"
                type="number"
                min="0"
                step="0.01"
                value={formData.amount}
                onChange={handleFieldChange}
                placeholder="2500.00"
                className="w-full rounded-lg border border-[var(--gridline)] bg-[var(--surface-2)] px-3 py-2.5 text-[var(--text-primary)] placeholder:text-[var(--text-muted)] outline-none transition-colors focus:border-[var(--primary)]"
              />
            </div>
          ) : (
            <div className="grid gap-5 md:grid-cols-2">
              <div>
                <label htmlFor="quantity" className="mb-2 block text-sm font-medium text-[var(--text-primary)]">
                  Quantity
                </label>
                <input
                  id="quantity"
                  name="quantity"
                  type="number"
                  min="0"
                  step="0.01"
                  value={formData.quantity}
                  onChange={handleFieldChange}
                  placeholder="10"
                  className="w-full rounded-lg border border-[var(--gridline)] bg-[var(--surface-2)] px-3 py-2.5 text-[var(--text-primary)] placeholder:text-[var(--text-muted)] outline-none transition-colors focus:border-[var(--primary)]"
                />
              </div>

              <div>
                <label htmlFor="price" className="mb-2 block text-sm font-medium text-[var(--text-primary)]">
                  Sale Price
                </label>
                <input
                  id="price"
                  name="price"
                  type="number"
                  min="0"
                  step="0.01"
                  value={formData.price}
                  onChange={handleFieldChange}
                  placeholder="214.75"
                  className="w-full rounded-lg border border-[var(--gridline)] bg-[var(--surface-2)] px-3 py-2.5 text-[var(--text-primary)] placeholder:text-[var(--text-muted)] outline-none transition-colors focus:border-[var(--primary)]"
                />
              </div>
            </div>
          )}

          <div>
            <label htmlFor="date" className="mb-2 block text-sm font-medium text-[var(--text-primary)]">
              Date of Transaction
            </label>
            <input
              id="date"
              name="date"
              type="date"
              value={formData.date}
              onChange={handleFieldChange}
              className="w-full rounded-lg border border-[var(--gridline)] bg-[var(--surface-2)] px-3 py-2.5 text-[var(--text-primary)] outline-none transition-colors focus:border-[var(--primary)]"
            />
          </div>

          {error && (
            <div className="rounded-lg border border-[var(--status-serious)]/30 bg-[var(--status-serious)]/10 px-3 py-2 text-sm text-[var(--status-serious)]">
              {error}
            </div>
          )}

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={handleClose}
              className="rounded-lg border border-[var(--border)] bg-[var(--surface-2)] px-4 py-2.5 text-sm font-semibold text-[var(--text-primary)] hover:bg-[var(--surface-3)]"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="rounded-lg bg-[var(--primary)] px-4 py-2.5 text-sm font-semibold text-white hover:bg-[var(--primary-dark)] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {submitting ? 'Saving...' : 'Sell Asset'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default DeleteAssetModal
