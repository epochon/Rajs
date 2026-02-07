interface HeaderProps {
  ticker: string | null
}

export default function Header({ ticker }: HeaderProps) {
  return (
    <header className="border-b border-navy-700 bg-navy-900/90 px-6 py-4">
      <h1 className="text-xl font-semibold text-white">ArbiTickers</h1>
      <p className="mt-1 text-sm text-navy-400">
        {ticker ? `Ticker: ${ticker}` : 'Enter a ticker and run analysis'}
      </p>
    </header>
  )
}
