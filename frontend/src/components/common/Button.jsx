const BASE =
  'rounded-lg font-semibold transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0 disabled:hover:shadow-none'

const VARIANTS = {
  primary:
    'bg-[var(--primary)] text-white hover:bg-[var(--primary-dark)] hover:shadow-md hover:-translate-y-0.5 active:translate-y-0',
  secondary:
    'border border-[var(--border)] bg-[var(--surface-2)] text-[var(--text-primary)] hover:bg-[var(--surface-3)] hover:shadow-md hover:-translate-y-0.5 active:translate-y-0',
  outline:
    'border border-[var(--primary)] bg-[var(--primary)]/10 text-[var(--primary)] hover:bg-[var(--primary)]/20 hover:shadow-md',
}

const SIZES = {
  sm: 'px-4 py-2 text-xs',
  md: 'px-5 py-2 text-sm',
}

/**
 * Defaults to `type="button"`. A bare `<button>` inside a `<form>` submits it, which is the
 * usual cause of "my cancel button reloads the page" — opting in to submit is the safer default.
 */
function Button({ variant = 'primary', size = 'md', type = 'button', className = '', ...props }) {
  return (
    <button
      type={type}
      className={`${BASE} ${VARIANTS[variant]} ${SIZES[size]} ${className}`}
      {...props}
    />
  )
}

export default Button
