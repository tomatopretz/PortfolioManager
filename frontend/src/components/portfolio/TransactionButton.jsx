import { useState } from 'react'
import { usePortfolioContext } from '../../context/PortfolioContext'
import Button from '../common/Button'
import TransactionModal from './TransactionModal'

const MODES = {
  buy: { label: 'Add Asset', variant: 'primary' },
  sell: { label: 'Remove Asset', variant: 'secondary' },
}

/** Button + its transaction modal, wired to the portfolio context. */
function TransactionButton({ mode }) {
  const { buyAsset, sellAsset } = usePortfolioContext()
  const [isOpen, setIsOpen] = useState(false)

  const { label, variant } = MODES[mode]

  return (
    <>
      <Button variant={variant} onClick={() => setIsOpen(true)}>
        {label}
      </Button>

      <TransactionModal
        mode={mode}
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        onSubmit={mode === 'buy' ? buyAsset : sellAsset}
      />
    </>
  )
}

export default TransactionButton
