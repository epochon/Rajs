import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts'
import type { QuantData } from '../mockData'
import { mockPriceHistory } from '../mockData'

interface QuantSectionProps {
  quant: QuantData
}

function num(v: number | string): number | null {
  if (typeof v === 'number' && !Number.isNaN(v)) return v
  if (typeof v === 'string' && v !== 'N/A') {
    const n = parseFloat(v)
    return Number.isNaN(n) ? null : n
  }
  return null
}

export default function QuantSection({ quant }: QuantSectionProps) {
  const price = num(quant.current_price) ?? 0
  const priceHistory = mockPriceHistory(price)

  const rev = num(quant.revenue_growth_yoy_pct)
  const eps = num(quant.eps_growth_pct)
  const vol = num(quant.volatility_proxy)
  const barData = [
    { name: 'Revenue growth YoY %', value: rev ?? 0, fill: '#22c55e' },
    { name: 'EPS growth %', value: eps ?? 0, fill: '#9333ea' },
    { name: 'Volatility (ann.)', value: vol != null ? vol * 100 : 0, fill: '#eab308' },
  ].filter((d) => d.value !== 0 || d.name.includes('Volatility'))

  const pe = num(quant.pe_ratio)
  const cap = num(quant.market_cap)
  const ret30 = num(quant.return_30d_pct)

  return (
    <section className="rounded-lg border border-navy-600 bg-navy-800/50 p-4">
      <h2 className="mb-4 text-lg font-semibold text-slate-200">Quantitative data</h2>

      <div className="mb-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
        <div className="rounded bg-navy-800 p-3">
          <p className="text-xs text-navy-400">P/E</p>
          <p className="text-lg font-medium text-white">{pe != null ? pe.toFixed(1) : 'N/A'}</p>
        </div>
        <div className="rounded bg-navy-800 p-3">
          <p className="text-xs text-navy-400">Market cap</p>
          <p className="text-lg font-medium text-white">
            {cap != null ? `${(cap / 1e9).toFixed(1)}B` : 'N/A'}
          </p>
        </div>
        <div className="rounded bg-navy-800 p-3">
          <p className="text-xs text-navy-400">30D return</p>
          <p className="text-lg font-medium text-white">
            {ret30 != null ? `${ret30 > 0 ? '+' : ''}${ret30.toFixed(2)}%` : 'N/A'}
          </p>
        </div>
      </div>

      <div className="mb-4 h-48">
        <p className="mb-1 text-xs text-navy-400">Price (mock trend)</p>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={priceHistory}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2d4a6f" />
            <XAxis dataKey="date" tick={{ fontSize: 10 }} stroke="#5c7a9e" />
            <YAxis domain={['auto', 'auto']} tick={{ fontSize: 10 }} stroke="#5c7a9e" />
            <Tooltip contentStyle={{ backgroundColor: '#0d2137', border: '1px solid #2d4a6f' }} />
            <Line type="monotone" dataKey="close" stroke="#9333ea" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="h-40">
        <p className="mb-1 text-xs text-navy-400">Revenue growth · EPS growth · Volatility</p>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={barData} margin={{ top: 4, right: 4, left: 4, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2d4a6f" />
            <XAxis dataKey="name" tick={{ fontSize: 9 }} stroke="#5c7a9e" />
            <YAxis tick={{ fontSize: 10 }} stroke="#5c7a9e" />
            <Tooltip contentStyle={{ backgroundColor: '#0d2137', border: '1px solid #2d4a6f' }} />
            <Bar dataKey="value" radius={4} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  )
}
