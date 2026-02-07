import type { VerdictData } from '../mockData'

interface VerdictSectionProps {
  verdict: VerdictData
}

const VERDICT_COLORS: Record<string, string> = {
  BUY: 'bg-emerald-600 text-white border-emerald-500',
  HOLD: 'bg-amber-600 text-white border-amber-500',
  SELL: 'bg-accent-600 text-white border-accent-500',
}

export default function VerdictSection({ verdict }: VerdictSectionProps) {
  const colorClass = VERDICT_COLORS[verdict.verdict] ?? 'bg-navy-600'

  return (
    <section className="rounded-lg border border-navy-600 bg-navy-800/50 p-4">
      <h2 className="mb-3 text-lg font-semibold text-slate-200">Verdict</h2>
      <div className="mb-3 flex flex-wrap items-center gap-4">
        <span
          className={`inline-block rounded-lg border-2 px-6 py-2 text-2xl font-bold ${colorClass}`}
        >
          {verdict.verdict}
        </span>
        <div className="flex-1 min-w-[120px]">
          <p className="mb-1 text-xs text-navy-400">Confidence (0–100)</p>
          <div className="h-6 w-full overflow-hidden rounded-full bg-navy-700">
            <div
              className="h-full rounded-full bg-accent-500 transition-all duration-500"
              style={{ width: `${Math.min(100, Math.max(0, verdict.confidence_score))}%` }}
            />
          </div>
          <p className="mt-1 text-xs text-navy-400">{verdict.confidence_score}</p>
        </div>
      </div>
      {verdict.justification?.length > 0 && (
        <ul className="mb-3 list-disc space-y-1 pl-4 text-sm text-navy-400">
          {verdict.justification.map((j, i) => (
            <li key={i}>{j}</li>
          ))}
        </ul>
      )}
      <p className="text-xs text-navy-400">{verdict.confidence_basis}</p>
      <p className="mt-3 border-t border-navy-600 pt-3 text-xs italic text-navy-400">
        This output is for decision support only and does not constitute financial advice. Do your
        own research and consider consulting a licensed advisor.
      </p>
    </section>
  )
}
