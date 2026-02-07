interface BullPanelProps {
  content: string
}

/** Renders Bull (Growth Advocate) output with green accent and clean bullets. */
export default function BullPanel({ content }: BullPanelProps) {
  const paragraphs = content.split(/\n\n+/).filter(Boolean)

  return (
    <section className="rounded-lg border-2 border-bull-border bg-bull-bg p-4">
      <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold text-bull-text">
        <span aria-hidden>🐂</span> Bull — Growth Advocate
      </h2>
      <div className="space-y-2 text-sm text-slate-300">
        {paragraphs.map((p, i) => (
          <p key={i}>{p.trim()}</p>
        ))}
      </div>
    </section>
  )
}
