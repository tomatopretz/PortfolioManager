import { useState } from 'react'
import Modal from '../common/Modal'
import Button from '../common/Button'
import {
  CheckboxField,
  FormError,
  NumberField,
  SelectField,
  TextField,
} from '../common/FormControls'
import { ASSET_TYPE_OPTIONS, CASH_ASSET_TYPE } from '../../constants/portfolio'
import { todayIso } from '../../utils/format'

// Buy and sell are the same form; only the copy and the "use cash balance" toggle differ.
const MODES = {
  buy: {
    title: 'Add Asset',
    submitLabel: 'Add Asset',
    cashAmountLabel: 'Amount',
    priceLabel: 'Price',
    invalidCashAmount: 'Please enter a valid cash amount.',
    genericError: 'Unable to add this asset.',
    offersCashToggle: true,
  },
  sell: {
    title: 'Sell Asset',
    submitLabel: 'Sell Asset',
    cashAmountLabel: 'Withdrawal Amount',
    priceLabel: 'Sale Price',
    invalidCashAmount: 'Please enter a valid withdrawal amount.',
    genericError: 'Unable to sell this asset.',
    offersCashToggle: false,
  },
}

const createFormState = () => ({
  ticker: '',
  assetType: 'stock',
  quantity: '',
  price: '',
  amount: '',
  useCash: true,
  date: todayIso(),
})

const buildPayload = (mode, formData, isCashAsset) => ({
  type: mode,
  ticker: isCashAsset ? 'USD' : formData.ticker.trim().toUpperCase(),
  assetType: formData.assetType,
  quantity: Number(isCashAsset ? formData.amount : formData.quantity),
  price: isCashAsset ? 1 : Number(formData.price),
  ...(MODES[mode].offersCashToggle ? { useCash: isCashAsset ? true : formData.useCash } : {}),
  date: formData.date,
})

const validate = (payload, config, isCashAsset) => {
  if (isCashAsset) {
    if (!payload.quantity || payload.quantity <= 0) return config.invalidCashAmount
    return null
  }
  if (!payload.ticker) return 'Ticker is required.'
  if (!payload.quantity || payload.quantity <= 0) return 'Quantity must be greater than zero.'
  if (!Number.isInteger(payload.quantity)) return 'Quantity must be a whole number of units.'
  if (!payload.price || payload.price <= 0) return 'Price must be greater than zero.'
  return null
}

function TransactionModal({ mode, isOpen, onClose, onSubmit }) {
  const config = MODES[mode]
  const [formData, setFormData] = useState(createFormState)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const isCashAsset = formData.assetType === CASH_ASSET_TYPE

  const handleFieldChange = (event) => {
    const { name, value, type, checked } = event.target
    setFormData((current) => ({ ...current, [name]: type === 'checkbox' ? checked : value }))
    setError('')
  }

  const handleClose = () => {
    setFormData(createFormState())
    setError('')
    onClose()
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSubmitting(true)
    setError('')

    try {
      const payload = buildPayload(mode, formData, isCashAsset)
      const validationError = validate(payload, config, isCashAsset)
      if (validationError) throw new Error(validationError)

      const result = await onSubmit(payload)
      if (!result?.success) throw new Error(result?.error || config.genericError)

      handleClose()
    } catch (submitError) {
      setError(submitError.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      eyebrow="New Transaction"
      title={config.title}
      closeLabel={`Close ${config.title.toLowerCase()} form`}
    >
      <form onSubmit={handleSubmit} className="space-y-5">
        <SelectField
          name="assetType"
          label="Asset Type"
          value={formData.assetType}
          onChange={handleFieldChange}
          options={ASSET_TYPE_OPTIONS}
        />

        {!isCashAsset && (
          <TextField
            name="ticker"
            label="Ticker"
            type="text"
            value={formData.ticker}
            onChange={handleFieldChange}
            placeholder="AAPL"
          />
        )}

        {isCashAsset ? (
          <NumberField
            name="amount"
            label={config.cashAmountLabel}
            value={formData.amount}
            onChange={handleFieldChange}
            placeholder="2500.00"
          />
        ) : (
          <div className="grid gap-5 md:grid-cols-2">
            <NumberField
              name="quantity"
              label="Quantity"
              value={formData.quantity}
              onChange={handleFieldChange}
              min="1"
              step="1"
              placeholder="10"
            />
            <NumberField
              name="price"
              label={config.priceLabel}
              value={formData.price}
              onChange={handleFieldChange}
              placeholder="214.75"
            />
          </div>
        )}

        {config.offersCashToggle && !isCashAsset && (
          <CheckboxField
            name="useCash"
            label="Use cash balance for this transaction"
            checked={formData.useCash}
            onChange={handleFieldChange}
          />
        )}

        <TextField
          name="date"
          label="Date of Transaction"
          type="date"
          value={formData.date}
          onChange={handleFieldChange}
        />

        <FormError>{error}</FormError>

        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={handleClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={submitting}>
            {submitting ? 'Saving...' : config.submitLabel}
          </Button>
        </div>
      </form>
    </Modal>
  )
}

export default TransactionModal
