/**
 * Mock response matching backend CLI/API output (AMD-style).
 * Replace fetchAnalysis() body with real API call when backend exposes JSON.
 */
export interface QuantData {
  ticker: string
  current_price: number
  pe_ratio: number
  market_cap: number
  revenue_growth_yoy_pct: number | string
  eps_growth_pct: number | string
  return_30d_pct: number | string
  range_52w_low: number | string
  range_52w_high: number | string
  range_52w_position: number | string
  volatility_proxy: number | string
  data_available: boolean
}

export interface VerdictData {
  verdict: 'BUY' | 'HOLD' | 'SELL'
  confidence_score: number
  justification: string[]
  confidence_basis: string
}

export interface AnalysisResult {
  ticker: string
  bear_output: string
  bull_output: string
  quant_data: QuantData
  verdict: VerdictData
}

/** Mock price history for line chart (last 30 points). */
export function mockPriceHistory(price: number): { date: string; close: number }[] {
  const out = []
  let p = price * 0.92
  for (let i = 30; i >= 0; i--) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    p += (Math.random() - 0.48) * price * 0.02
    out.push({ date: d.toISOString().slice(0, 10), close: Math.round(p * 100) / 100 })
  }
  return out
}

/** Default mock result (AMD-style). Use for demo when no backend. */
export const MOCK_RESULT: AnalysisResult = {
  ticker: 'AMD',
  bear_output: `* Regulatory:
  + Changes in US export control regulations affecting sales to key customers
  + Potential antitrust lawsuits or investigations
  + Compliance risks related to data protection and privacy regulations
* Valuation:
  + Overvaluation due to high price-to-earnings ratio
  + Volatility in stock price due to market sentiment
  + Potential decline in earnings multiple
* Competitive:
  + Intensifying competition from Intel and Nvidia in CPU and GPU markets
  + Competition from Asian semiconductor manufacturers
  + Risk of losing market share to competitors
* Macro:
  + Global economic downturn affecting demand for PCs and electronics
  + Trade tensions and tariffs impacting international trade
  + Fluctuations in currency exchange rates affecting export sales`,
  bull_output: `I acknowledge the Bear's concerns regarding AMD, including regulatory risks (export controls, antitrust, compliance), valuation concerns (high P/E, volatility), competitive pressure from Intel and Nvidia, and macro risks (economic downturn, trade tensions).

However, AMD has been gaining market share in CPU and GPU markets, driven by strong product lineup and improving manufacturing. Investments in R&D have made products more competitive. Expansion into data centers and gaming consoles provides growth and diversification. Demand for AI, ML, and cloud computing bodes well for high-performance computing. While risks exist, AMD's strong product portfolio, growing market share, and expanding addressable market provide a compelling growth narrative.`,
  quant_data: {
    ticker: 'AMD',
    current_price: 208.44,
    pe_ratio: 79.86,
    market_cap: 339842859008,
    revenue_growth_yoy_pct: 34.1,
    eps_growth_pct: 217.1,
    return_30d_pct: -0.75,
    range_52w_low: 76.48,
    range_52w_high: 267.08,
    range_52w_position: 0.69,
    volatility_proxy: 0.64,
    data_available: true,
  },
  verdict: {
    verdict: 'HOLD',
    confidence_score: 49,
    justification: [
      'Revenue growth YoY +34.1% adds support (+15 pts).',
      'EPS growth +217.1% adds support (+10 pts).',
      '30-day return -0.75% subtracts points (-1 pts).',
      'High P/E (80) reduces score (-15 pts).',
      'Elevated volatility (0.64) reduces score (-10 pts).',
    ],
    confidence_basis: 'Data completeness: high (7/7 key metrics). Volatility: high. Valuation certainty: P/E available.',
  },
}

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

/** Fetch analysis from Python backend. Falls back to mock only if API is unreachable (network error). */
export async function fetchAnalysis(ticker: string): Promise<AnalysisResult> {
  const url = `${API_BASE}/api/analyze?ticker=${encodeURIComponent(ticker.trim().toUpperCase())}`
  try {
    const res = await fetch(url)
    if (!res.ok) {
      const errText = await res.text()
      let msg = errText || res.statusText
      try {
        const j = JSON.parse(errText)
        if (j.detail) msg = j.detail
      } catch {
        /* use raw text */
      }
      throw new Error(msg)
    }
    const data = await res.json()
    return data as AnalysisResult
  } catch (e) {
    if (e instanceof Error && !(e instanceof TypeError)) {
      throw e // rethrow validation/API errors (e.g. ticker not found); TypeError = network failure
    }
    console.warn('API unavailable, using mock data:', e)
    const q = { ...MOCK_RESULT.quant_data, ticker: ticker.toUpperCase() }
    return {
      ...MOCK_RESULT,
      ticker: ticker.toUpperCase(),
      quant_data: q,
    }
  }
}
