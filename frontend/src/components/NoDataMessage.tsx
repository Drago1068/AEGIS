/**
 * Phase 0 placeholder state. No charts, scores, or recommendations exist yet; this
 * component only communicates that the platform has no data to show.
 */
export function NoDataMessage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-8 text-center">
      <h1 className="text-2xl font-semibold">AEGIS 3.0</h1>
      <p className="text-base text-neutral-600">
        No data yet. Phase 0 establishes architecture, tooling, and infrastructure only.
      </p>
    </main>
  );
}
