import { DailyBar } from "@/lib/api-client";

type DailyBarsTableProps = {
  symbol: string;
  bars: DailyBar[];
};

export function DailyBarsTable({ symbol, bars }: DailyBarsTableProps) {
  if (bars.length === 0) {
    return (
      <p className="text-sm text-aegis-muted">
        No stored daily bars for {symbol}. Run ingest after adding the symbol to the watchlist.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-left text-sm">
        <thead className="border-b border-aegis-line text-aegis-muted">
          <tr>
            <th className="py-2 pr-4 font-medium">Date</th>
            <th className="py-2 pr-4 font-medium">Open</th>
            <th className="py-2 pr-4 font-medium">High</th>
            <th className="py-2 pr-4 font-medium">Low</th>
            <th className="py-2 pr-4 font-medium">Close</th>
            <th className="py-2 pr-4 font-medium">Volume</th>
            <th className="py-2 font-medium">Quality</th>
          </tr>
        </thead>
        <tbody>
          {bars.map((bar) => (
            <tr key={`${bar.symbol}-${bar.trading_date}`} className="border-b border-aegis-line/70">
              <td className="py-2 pr-4 font-mono">{bar.trading_date}</td>
              <td className="py-2 pr-4 font-mono">{bar.open}</td>
              <td className="py-2 pr-4 font-mono">{bar.high}</td>
              <td className="py-2 pr-4 font-mono">{bar.low}</td>
              <td className="py-2 pr-4 font-mono">{bar.close}</td>
              <td className="py-2 pr-4 font-mono">{bar.volume}</td>
              <td className="py-2">{bar.data_quality}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
