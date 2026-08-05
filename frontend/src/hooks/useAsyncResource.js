import { useCallback, useRef, useState } from 'react'

/**
 * Loads data from an async `fetcher`, tracking loading/error state.
 *
 * Every call gets a monotonic id and only the newest one is allowed to write state, so a slow
 * response that resolves after a newer one can't clobber it (or leave the spinner stuck on).
 *
 * Two ways in: `load` for a first/blocking fetch (flags `loading`, which callers use to swap in
 * a spinner) and `refresh` for a re-fetch of data already on screen (flags `refreshing` instead,
 * so the current values stay rendered rather than flashing back to a spinner).
 *
 * `fetcher` must be referentially stable — pass a module-level function or a `useCallback`.
 */
export const useAsyncResource = (fetcher, initialData) => {
  const [data, setData] = useState(initialData)
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState(null)
  const [lastUpdatedAt, setLastUpdatedAt] = useState(null)
  const latestRequestId = useRef(0)

  const run = useCallback(
    async (setBusy, args) => {
      const requestId = ++latestRequestId.current
      setBusy(true)
      setError(null)
      try {
        const result = await fetcher(...args)
        if (requestId !== latestRequestId.current) return
        setData(result)
        setLastUpdatedAt(Date.now())
      } catch (err) {
        if (requestId !== latestRequestId.current) return
        setError(err.message)
      } finally {
        // The newest call clears both flags, not just its own: a superseded call returns
        // without clearing anything, so whichever flag it raised would otherwise stay stuck
        // on (e.g. a refresh clicked while the initial load is still in flight).
        if (requestId === latestRequestId.current) {
          setLoading(false)
          setRefreshing(false)
        }
      }
    },
    [fetcher]
  )

  const load = useCallback((...args) => run(setLoading, args), [run])
  const refresh = useCallback((...args) => run(setRefreshing, args), [run])

  return { data, setData, loading, refreshing, error, lastUpdatedAt, load, refresh }
}
