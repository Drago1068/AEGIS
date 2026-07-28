import { redirect } from "next/navigation";

import { IngestPanel } from "@/components/IngestPanel";
import { OperatorSessionBar } from "@/components/OperatorSessionBar";
import { WatchlistPanel } from "@/components/WatchlistPanel";
import { ApiClientError, getApiBaseUrl, listWatchlist } from "@/lib/api-client";
import { requireOperator } from "@/lib/require-operator";

export const dynamic = "force-dynamic";

async function loadWatchlist(cookie?: string) {
  try {
    const symbols = await listWatchlist(getApiBaseUrl(), { cookie });
    return { symbols, error: null as string | null };
  } catch (err) {
    if (err instanceof ApiClientError && err.status === 401) {
      redirect("/login");
    }
    const message =
      err instanceof ApiClientError
        ? err.message
        : "Could not load the watchlist from the backend.";
    return { symbols: [], error: message };
  }
}

export default async function HomePage() {
  const { username, cookie } = await requireOperator();
  const { symbols, error } = await loadWatchlist(cookie);

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-5xl flex-col gap-8 px-6 py-10">
      <header className="space-y-2">
        <p className="text-sm font-medium uppercase tracking-[0.18em] text-aegis-accent">
          Decision support
        </p>
        <h1 className="text-4xl font-semibold tracking-tight text-aegis-ink md:text-5xl">AEGIS</h1>
        <p className="max-w-2xl text-base text-aegis-muted md:text-lg">
          Operator console for the active watchlist and on-demand market data ingestion. No
          live orders are placed from this application.
        </p>
        <OperatorSessionBar username={username} />
      </header>

      <div className="grid gap-6 lg:grid-cols-2">
        <WatchlistPanel initialSymbols={symbols} loadError={error} />
        <IngestPanel />
      </div>
    </main>
  );
}
