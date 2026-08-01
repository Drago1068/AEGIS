/**
 * Adapters for rendering assessment research_index history with Lightweight Charts.
 *
 * The assessments list API returns newest-first; the chart library requires
 * chronological (oldest-first) series data. Skip empty/non-finite values; do not invent.
 * See ADR-0300.
 */

export type ResearchIndexHistoryPoint = {
  time: string;
  value: number;
};

export type ResearchIndexHistoryInput = {
  as_of_trading_date: string;
  components: {
    research_index?: unknown;
    [key: string]: unknown;
  };
};

const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;

/**
 * Map assessments list rows (newest-first) to chronological research_index points.
 *
 * Fail-closed: skips missing/invalid dates and non-finite research_index.
 * Duplicate as_of dates keep the newest row (first seen in newest-first order).
 */
export function toResearchIndexHistoryChartData(
  assessments: ResearchIndexHistoryInput[],
): ResearchIndexHistoryPoint[] {
  const byDate = new Map<string, number>();

  for (const row of assessments) {
    const date = row.as_of_trading_date;
    if (typeof date !== "string" || !ISO_DATE.test(date)) {
      continue;
    }
    if (byDate.has(date)) {
      continue;
    }
    const index = row.components.research_index;
    if (typeof index !== "number" || !Number.isFinite(index)) {
      continue;
    }
    byDate.set(date, index);
  }

  return [...byDate.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([time, value]) => ({ time, value }));
}
