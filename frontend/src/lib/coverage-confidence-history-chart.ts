/**
 * Adapters for rendering assessment coverage_confidence history with Lightweight Charts.
 *
 * The assessments list API returns newest-first; the chart library requires
 * chronological (oldest-first) series data. Skip empty/non-finite values; do not invent.
 * Coverage confidence is distinct from probability_confidence and research_index.
 * See ADR-0304.
 */

export type CoverageConfidenceHistoryPoint = {
  time: string;
  value: number;
};

export type CoverageConfidenceHistoryInput = {
  as_of_trading_date: string;
  coverage_confidence?: unknown;
};

const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;

/**
 * Map assessments list rows (newest-first) to chronological coverage_confidence points.
 *
 * Fail-closed: skips missing/invalid dates and non-finite coverage_confidence.
 * Duplicate as_of dates keep the newest row (first seen in newest-first order).
 * Never reads probability_confidence.
 */
export function toCoverageConfidenceHistoryChartData(
  assessments: CoverageConfidenceHistoryInput[],
): CoverageConfidenceHistoryPoint[] {
  const byDate = new Map<string, number>();

  for (const row of assessments) {
    const date = row.as_of_trading_date;
    if (typeof date !== "string" || !ISO_DATE.test(date)) {
      continue;
    }
    if (byDate.has(date)) {
      continue;
    }
    const coverage = row.coverage_confidence;
    if (typeof coverage !== "number" || !Number.isFinite(coverage)) {
      continue;
    }
    byDate.set(date, coverage);
  }

  return [...byDate.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([time, value]) => ({ time, value }));
}
