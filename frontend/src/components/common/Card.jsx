const BASE =
  'rounded-xl border border-[var(--border)] bg-[var(--surface-1)] shadow-[var(--shadow-sm)]'

const INTERACTIVE =
  'transition-all duration-200 hover:border-[var(--primary)] hover:shadow-[var(--shadow-md)]'

/**
 * Surface panel used for every boxed section. `padding` is a prop rather than part of
 * `className` so callers can't accidentally ship two conflicting Tailwind padding utilities.
 */
function Card({ padding = 'p-6', interactive = false, className = '', children }) {
  return (
    <div className={`${BASE} ${padding} ${interactive ? INTERACTIVE : ''} ${className}`}>
      {children}
    </div>
  )
}

export default Card
