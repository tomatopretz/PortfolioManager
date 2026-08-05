import { useEffect } from 'react'

/**
 * Dialog shell: backdrop, escape-to-close, background scroll lock and a titled header.
 * Body content (usually a form) is supplied by the caller.
 */
function Modal({ isOpen, onClose, eyebrow, title, closeLabel = 'Close dialog', children }) {
  useEffect(() => {
    if (!isOpen) return undefined

    const handleKeyDown = (event) => {
      if (event.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handleKeyDown)

    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = previousOverflow
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  // Only a click that starts and ends on the backdrop itself dismisses; clicks bubbling up
  // from inside the panel must not.
  const handleBackdropClick = (event) => {
    if (event.target === event.currentTarget) onClose()
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4 backdrop-blur-sm"
      onClick={handleBackdropClick}
      role="presentation"
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className="max-h-[90vh] w-full max-w-xl overflow-y-auto rounded-2xl border border-[var(--border)] bg-[var(--surface-1)] p-6 shadow-[var(--shadow-lg)]"
      >
        <div className="mb-6 flex items-center justify-between">
          <div>
            {eyebrow && (
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[var(--text-secondary)]">
                {eyebrow}
              </p>
            )}
            <h2 className="mt-1 text-2xl font-bold text-[var(--text-primary)]">{title}</h2>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-full border border-[var(--border)] bg-[var(--surface-2)] p-2 text-[var(--text-secondary)] hover:bg-[var(--surface-3)]"
            aria-label={closeLabel}
          >
            ✕
          </button>
        </div>

        {children}
      </div>
    </div>
  )
}

export default Modal
