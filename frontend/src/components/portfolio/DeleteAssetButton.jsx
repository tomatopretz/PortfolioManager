import { useState } from 'react'
import { usePortfolioContext } from '../../context/PortfolioContext'
import DeleteAssetModal from './DeleteAssetModal'

function DeleteAssetButton() {
  const { handleSell } = usePortfolioContext()
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className="rounded-lg border border-[var(--border)] bg-[var(--surface-2)] px-5 py-2 text-sm font-semibold text-[var(--text-primary)] transition-all duration-200 hover:bg-[var(--surface-3)] hover:shadow-md hover:-translate-y-0.5 active:translate-y-0"
      >
        Remove Asset
      </button>

      <DeleteAssetModal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        onSubmit={handleSell}
      />
    </>
  )
}

export default DeleteAssetButton
