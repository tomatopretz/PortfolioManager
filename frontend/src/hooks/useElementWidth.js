import { useCallback, useState } from 'react'

/**
 * Tracks the rendered width of an element, for layout decisions that depend on the space a
 * component actually got rather than on the viewport (e.g. a chart inside a card that narrows on
 * smaller screens).
 *
 * Returns `[ref, width]`, where `width` is `null` until the node is measured. The ref is a
 * callback ref so observation starts the moment the node mounts and is torn down when it
 * unmounts - no separate effect that can run a render too late.
 */
export const useElementWidth = () => {
  const [width, setWidth] = useState(null)

  const ref = useCallback((node) => {
    if (!node) {
      setWidth(null)
      return undefined
    }

    setWidth(node.getBoundingClientRect().width)
    const observer = new ResizeObserver(([entry]) => setWidth(entry.contentRect.width))
    observer.observe(node)
    return () => observer.disconnect()
  }, [])

  return [ref, width]
}
