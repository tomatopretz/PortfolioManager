const STAR_PATH =
  'M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.562.562 0 00-.586 0l-4.725 2.885a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557L2.043 10.386a.562.562 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z'

const BASE = 'inline-flex h-5 w-5 items-center justify-center'

function StarIcon({ filled }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill={filled ? 'currentColor' : 'none'}
      stroke="currentColor"
      strokeWidth="1.5"
      className="h-4 w-4"
      aria-hidden="true"
    >
      <path strokeLinecap="round" strokeLinejoin="round" d={STAR_PATH} />
    </svg>
  )
}

function FavouriteStar({
  active,
  onToggle,
  disabled = false,
  disabledReason = 'This holding cannot be favourited',
}) {
  if (disabled) {
    return (
      <span className={`${BASE} text-[var(--text-muted)] opacity-40`} title={disabledReason}>
        <StarIcon filled={false} />
      </span>
    )
  }

  return (
    <button
      type="button"
      onClick={onToggle}
      aria-pressed={active}
      aria-label={active ? 'Remove from favourites' : 'Add to favourites'}
      className={`${BASE} transition-colors ${
        active
          ? 'text-[var(--status-warning)]'
          : 'text-[var(--text-muted)] hover:text-[var(--status-warning)]'
      }`}
    >
      <StarIcon filled={active} />
    </button>
  )
}

export default FavouriteStar
