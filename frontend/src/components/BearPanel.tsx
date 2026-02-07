interface BearPanelProps {
  content: string
}

/** Renders Bear (Risk Analyst) output with red accent and clean bullets. */
export default function BearPanel({ content }: BearPanelProps) {
  const lines = content.split('\n').filter(Boolean)

  return (
    <section className="rounded-lg border-2 border-bear-border bg-bear-bg p-4">
      <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold text-bear-text">
        <span aria-hidden>🐻</span> Bear — Risk Analyst
      </h2>
      <ul className="space-y-1.5 text-sm text-slate-300">
        {lines.map((line, i) => {
          const isBullet = line.trimStart().startsWith('*') || line.trimStart().startsWith('+')
          const text = line.replace(/^\s*[\*\+]\s*/, '').trim()
          if (!text) return null
          return (
            <li key={i} className={isBullet ? 'list-disc pl-4' : ''}>
              {text}
            </li>
          )
        })}
      </ul>
    </section>
  )
}
