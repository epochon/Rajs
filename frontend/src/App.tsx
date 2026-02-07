import { useState } from 'react'
import type { Profile } from './api'
import Header from './components/Header'
import TickerInput from './components/TickerInput'
import BearPanel from './components/BearPanel'
import BullPanel from './components/BullPanel'
import QuantSection from './components/QuantSection'
import VerdictSection from './components/VerdictSection'
import ProfileSelector from './components/ProfileSelector'
import WatchlistSection from './components/WatchlistSection'
import { fetchAnalysis, type AnalysisResult } from './mockData'

export default function App() {
  const [ticker, setTicker] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [analyzeError, setAnalyzeError] = useState<string | null>(null)
  const [selectedProfile, setSelectedProfile] = useState<Profile | null>(null)

  const handleAnalyze = async (t: string) => {
    setLoading(true)
    setResult(null)
    setAnalyzeError(null)
    setTicker(t)
    try {
      const data = await fetchAnalysis(t)
      setResult(data)
    } catch (e) {
      setAnalyzeError(e instanceof Error ? e.message : 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen">
      <Header ticker={ticker} />
      <main className="mx-auto max-w-6xl px-4 py-6">
        <div className="mb-6 space-y-4">
          <ProfileSelector
            selectedId={selectedProfile?.id ?? null}
            onSelect={setSelectedProfile}
          />
          <WatchlistSection
            profile={selectedProfile}
            onProfileUpdate={setSelectedProfile}
            onAnalyzeTicker={(t) => handleAnalyze(t)}
          />
        </div>

        <div className="mb-6">
          <TickerInput onAnalyze={handleAnalyze} loading={loading} />
        </div>

        {analyzeError && (
          <div className="mb-6 rounded border border-accent-500/80 bg-accent-900/40 px-4 py-3 text-sm text-accent-300">
            {analyzeError}
          </div>
        )}

        {loading && (
          <div className="rounded-lg border border-navy-600 bg-navy-800/50 p-8 text-center text-navy-400">
            Running analysis…
          </div>
        )}

        {!loading && result && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              <BearPanel content={result.bear_output} />
              <BullPanel content={result.bull_output} />
            </div>
            <QuantSection quant={result.quant_data} />
            <VerdictSection verdict={result.verdict} />
          </div>
        )}

        {!loading && !result && ticker && !analyzeError && (
          <div className="rounded-lg border border-navy-600 bg-navy-800/50 p-6 text-center text-navy-400">
            No result yet. Click Analyze.
          </div>
        )}
      </main>
    </div>
  )
}
