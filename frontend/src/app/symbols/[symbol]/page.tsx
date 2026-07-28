import Link from "next/link";

import { DailyBarsTable } from "@/components/DailyBarsTable";
import { ApiClientError, getApiBaseUrl, listDailyBars } from "@/lib/api-client";

export const dynamic = "force-dynamic";

type SymbolPageProps = {
  params: Promise<{ symbol: string }>;
};

export default async function SymbolPage({ params }: SymbolPageProps) {
  const { symbol: rawSymbol } = await params;
  const symbol = decodeURIComponent(rawSymbol).toUpperCase();

  let bars: Awaited<ReturnType<typeof listDailyBars>> = [];
  let error: string | null = null;
  try {
    bars = await listDailyBars(getApiBaseUrl(), symbol);
  } catch (err) {
    if (err instanceof ApiClientError && err.status === 404) {
      bars = [];
    } else {
      error =
        err instanceof ApiClientError
          ? err.message
          : `Could not load daily bars for ${symbol}.`;
    }
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-5xl flex-col gap-6 px-6 py-10">
      <div className="space-y-2">
        <Link href="/" className="text-sm text-aegis-accent underline-offset-4 hover:underline">
          Back to console
        </Link>
        <h1 className="font-mono text-3xl font-semibold tracking-tight text-aegis-ink md:text-4xl">
          {symbol}
        </h1>
        <p className="text-base text-aegis-muted">Stored daily OHLCV observations (newest first)</p>
      </div>

      <section className="rounded-lg border border-aegis-line bg-aegis-panel p-5 shadow-sm">
        {error ? (
          <p className="text-sm text-aegis-danger" role="alert">
            {error}
          </p>
        ) : (
          <DailyBarsTable symbol={symbol} bars={bars} />
        )}
      </section>
    </main>
  );
}
