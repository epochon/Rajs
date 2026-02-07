import { useEffect, useRef, useState } from 'react'
import type { Profile } from '../api'
import type { CheckWatchlistResponse } from '../api'
import { checkWatchlist, updateProfileTickers } from '../api'

interface WatchlistSectionProps {
  profile: Profile | null
  onProfileUpdate: (profile: Profile) => void
  onAnalyzeTicker: (ticker: string) => void
}

const VERDICT_COLORS: Record<string, string> = {
  BUY: 'bg-emerald-600 text-white border-emerald-500',
  HOLD: 'bg-amber-600 text-white border-amber-500',
  SELL: 'bg-accent-600 text-white border-accent-500',
}

export default function WatchlistSection({
  profile,
  onProfileUpdate,
  onAnalyzeTicker,
}: WatchlistSectionProps) {
  const addRef = useRef<HTMLInputElement>(null)
  const [checking, setChecking] = useState(false)
  const [checkResult, setCheckResult] = useState<CheckWatchlistResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Clear previous results when switching profile
  useEffect(() => {
    setCheckResult(null)
    setError(null)
  }, [profile?.id])

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault()
    const t = addRef.current?.value?.trim().toUpperCase()
    if (!t || !profile) return
    setError(null)
    try {
      const updated = await updateProfileTickers(profile.id, [t], undefined)
      onProfileUpdate(updated)
      addRef.current!.value = ''
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add ticker. Is the backend running?')
    }
  }

  const handleRemove = async (ticker: string) => {
    if (!profile) return
    setError(null)
    try {
      const updated = await updateProfileTickers(profile.id, undefined, [ticker])
      onProfileUpdate(updated)
      setCheckResult((prev) =>
        prev
          ? {
              ...prev,
              results: prev.results.filter((r) => r.ticker !== ticker),
              good_to_invest: prev.good_to_invest.filter((t) => t !== ticker),
            }
          : null
      )
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove ticker.')
    }
  }

  const handleCheckWatchlist = async () => {
    if (!profile) return
    setChecking(true)
    setCheckResult(null)
    setError(null)
    try {
      const res = await checkWatchlist(profile.id)
      setCheckResult(res)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to check watchlist. Is the backend running?')
    } finally {
      setChecking(false)
    }
  }

  if (!profile) return null

  return (
    <div className="rounded-lg border border-navy-600 bg-navy-800/50 p-4">
      <h2 className="mb-3 text-lg font-semibold text-slate-200">Watchlist</h2>
      <p className="mb-3 text-sm text-navy-400">
        Add tickers to track. The AI will analyze them and notify when any have a <strong>BUY</strong> verdict.
      </p>

      {error && (
        <div className="mb-3 rounded border border-accent-500/80 bg-accent-900/40 px-3 py-2 text-sm text-accent-300">
          {error}
        </div>
      )}

      <form onSubmit={handleAdd} className="mb-4 flex flex-wrap items-end gap-2">
        <div className="min-w-[120px]">
          <label className="mb-1 block text-xs text-slate-400">Add ticker</label>
          <input
            ref={addRef}
            type="text"
            placeholder="e.g. AAPL"
            className="w-full rounded border border-navy-600 bg-navy-800 px-3 py-2 text-sm text-white placeholder-navy-400 focus:border-accent-500 focus:outline-none focus:ring-1 focus:ring-accent-500"
          />
        </div>
        <button
          type="submit"
          className="rounded bg-accent-600 px-3 py-2 text-sm font-medium text-white hover:bg-accent-500"
        >
          Add
        </button>
      </form>

      {profile.tickers.length > 0 && (
        <>
          <ul className="mb-3 flex flex-wrap gap-2">
            {profile.tickers.map((t) => (
              <li
                key={t}
                className="flex items-center gap-1 rounded bg-navy-700 px-2 py-1 text-sm text-slate-200"
              >
                <button
                  type="button"
                  onClick={() => onAnalyzeTicker(t)}
                  className="font-medium hover:text-sky-400 hover:underline"
                >
                  {t}
                </button>
                <button
                  type="button"
                  onClick={() => handleRemove(t)}
                  className="ml-1 text-navy-400 hover:text-accent-400"
                  aria-label={`Remove ${t}`}
                >
                  ×
                </button>
              </li>
            ))}
          </ul>
          <button
            type="button"
            onClick={handleCheckWatchlist}
            disabled={checking}
            className="rounded bg-accent-600 px-4 py-2 text-sm font-medium text-white hover:bg-accent-500 disabled:opacity-50"
          >
            {checking ? 'Checking watchlist…' : 'Check watchlist (run AI analysis)'}
          </button>
        </>
      )}

      {checkResult && (
        <div className="mt-4 space-y-3 border-t border-navy-600 pt-4">
          {checkResult.good_to_invest.length > 0 && (
            <div className="rounded-lg border-2 border-accent-600 bg-accent-900/30 p-4">
              <h3 className="mb-2 font-semibold text-accent-300">
                Good time to invest (BUY verdict)
              </h3>
              <p className="text-sm text-slate-200">
                The engine suggests these tickers may be a good time to consider:{' '}
                <strong className="text-accent-300">
                  {checkResult.good_to_invest.join(', ')}
                </strong>
              </p>
              <p className="mt-2 text-xs text-navy-400">
                Click a ticker above to see full analysis. This is decision support only, not financial advice.
              </p>
            </div>
          )}
          {checkResult.results.length > 0 && (
            <div>
              <h3 className="mb-2 text-sm font-medium text-navy-400">All results</h3>
              <ul className="space-y-2">
                {checkResult.results.map((r) => (
                  <li
                    key={r.ticker}
                    className="flex flex-wrap items-center gap-2 rounded border border-navy-600 bg-navy-800/80 px-3 py-2 text-sm"
                  >
                    <button
                      type="button"
                      onClick={() => onAnalyzeTicker(r.ticker)}
                      className="font-medium text-accent-400 hover:underline"
                    >
                      {r.ticker}
                    </button>
                    <span
                      className={`rounded border px-2 py-0.5 text-xs font-medium ${
                        VERDICT_COLORS[r.verdict] ?? 'bg-navy-600'
                      }`}
                    >
                      {r.verdict}
                    </span>
                    <span className="text-navy-400">({r.confidence_score})</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
