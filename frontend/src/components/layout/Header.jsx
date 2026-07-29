import { useState } from 'react'
import { TrendingUp } from 'lucide-react'

function Header() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <header className="bg-white border-b border-[var(--gridline)]">
      <div className="px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-6 h-6" style={{ color: 'var(--series-1)' }} />
          <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
            Portfolio Manager
          </h1>
        </div>

        <div className="flex items-center gap-6">
          <div className="flex gap-4 text-sm">
            <div>
              <p style={{ color: 'var(--text-muted)' }} className="text-xs">Cash Balance</p>
              <p className="font-semibold" style={{ color: 'var(--text-primary)' }}>$12,340.50</p>
            </div>
            <div>
              <p style={{ color: 'var(--text-muted)' }} className="text-xs">Portfolio Value</p>
              <p className="font-semibold" style={{ color: 'var(--text-primary)' }}>$148,220.75</p>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              className="px-4 py-2 bg-[var(--series-1)] text-white rounded hover:opacity-90"
              onClick={() => setIsOpen(!isOpen)}
            >
              Buy
            </button>
            <button
              className="px-4 py-2 border border-[var(--series-1)] text-[var(--series-1)] rounded hover:bg-blue-50"
              onClick={() => setIsOpen(!isOpen)}
            >
              Sell
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
