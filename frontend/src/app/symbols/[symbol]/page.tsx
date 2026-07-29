import Link from "next/link";

import { DailyBarsChart } from "@/components/DailyBarsChart";
import { DailyBarsTable } from "@/components/DailyBarsTable";
import { OperatorSessionBar } from "@/components/OperatorSessionBar";
import { ResearchAssessmentPanel } from "@/components/ResearchAssessmentPanel";
import {
  ApiClientError,
  getApiBaseUrl,
  getLatestResearchAssessment,
  listDailyBars,
} from "@/lib/api-client";
import { requireOperator } from "@/lib/require-operator";
import { redirect } from "next/navigation";

export const dynamic = "force-dynamic";

type SymbolPageProps = {
  params: Promise<{ symbol: string }>;
};

export default async function SymbolPage({ params }: SymbolPageProps) {
  const { username, cookie } = await requireOperator();
  const { symbol: rawSymbol } = await params;
  const symbol = decodeURIComponent(rawSymbol).toUpperCase();

  let bars: Awaited<ReturnType<typeof listDailyBars>> = [];
  let error: string | null = null;
  try {
    bars = await listDailyBars(getApiBaseUrl(), symbol, 100, { cookie });
  } catch (err) {
    if (err instanceof ApiClientError && err.status === 401) {
      redirect("/login");
    }
    if (err instanceof ApiClientError && err.status === 404) {
      bars = [];
    } else {
      error =
        err instanceof ApiClientError
          ? err.message
          : `Could not load daily bars for ${symbol}.`;
    }
  }

  let latestAssessment: Awaited<ReturnType<typeof getLatestResearchAssessment>> | null =
    null;
  try {
    latestAssessment = await getLatestResearchAssessment(getApiBaseUrl(), symbol, {
      cookie,
    });
  } catch (err) {
    if (err instanceof ApiClientError && err.status === 401) {
      redirect("/login");
    }
    if (!(err instanceof ApiClientError && err.status === 404)) {
      // Non-404 load failures leave the panel empty; the panel can still run on demand.
      latestAssessment = null;
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
        <OperatorSessionBar username={username} />
      </div>

      <section className="rounded-lg border border-aegis-line bg-aegis-panel p-5 shadow-sm">
        {error ? (
          <p className="text-sm text-aegis-danger" role="alert">
            {error}
          </p>
        ) : (
          <div className="flex flex-col gap-6">
            <DailyBarsChart symbol={symbol} bars={bars} />
            <DailyBarsTable symbol={symbol} bars={bars} />
          </div>
        )}
      </section>

      <ResearchAssessmentPanel symbol={symbol} initialLatest={latestAssessment} />
    </main>
  );
}
