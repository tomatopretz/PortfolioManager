import { useState } from 'react'
import { usePortfolioContext } from '../../context/PortfolioContext'
import AddAssetModal from './AddAssetModal'

function AddAssetButton() {
  const { handleBuy } = usePortfolioContext()
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className="rounded-lg bg-[var(--primary)] px-5 py-2 text-sm font-semibold text-white transition-all duration-200 hover:bg-[var(--primary-dark)] hover:shadow-md hover:-translate-y-0.5 active:translate-y-0"
      >
        Add Asset
      </button>

      <AddAssetModal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        onSubmit={handleBuy}
      />
    </>
  )
}

export default AddAssetButton
