import { useCallback, useRef, useState } from 'react'

/**
 * Loads data from an async `fetcher`, tracking loading/error state.
 *
 * Every call gets a monotonic id and only the newest one is allowed to write state, so a slow
 * response that resolves after a newer one can't clobber it (or leave the spinner stuck on).
 *
 * `fetcher` must be referentially stable — pass a module-level function or a `useCallback`.
 */
export const useAsyncResource = (fetcher, initialData) => {
  const [data, setData] = useState(initialData)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const latestRequestId = useRef(0)

  const load = useCallback(
    async (...args) => {
      const requestId = ++latestRequestId.current
      setLoading(true)
      setError(null)
      try {
        const result = await fetcher(...args)
        if (requestId !== latestRequestId.current) return
        setData(result)
      } catch (err) {
        if (requestId !== latestRequestId.current) return
        setError(err.message)
      } finally {
        if (requestId === latestRequestId.current) setLoading(false)
      }
    },
    [fetcher]
  )

  return { data, setData, loading, error, load }
}
