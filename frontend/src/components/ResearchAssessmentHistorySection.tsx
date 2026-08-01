"use client";

import type { ResearchAssessment } from "@/lib/api-client";

import { ResearchIndexHistoryChart } from "./ResearchIndexHistoryChart";
import {
  ASSESSMENT_SOURCE_FILTER_OPTIONS,
  formatAssessmentHistoryRow,
} from "./research-assessment-panel-helpers";

export type ResearchAssessmentHistorySectionProps = {
  assessmentHistory: ResearchAssessment[];
  assessmentSourceFilter: string;
  isPending: boolean;
  onAssessmentSourceFilterChange: (value: string) => void;
  symbol: string;
};

export function ResearchAssessmentHistorySection({
  assessmentHistory,
  assessmentSourceFilter,
  isPending,
  onAssessmentSourceFilterChange,
  symbol,
}: ResearchAssessmentHistorySectionProps) {
  return (
    <div
      id="assessment-history"
      className="rounded border border-aegis-line bg-white/60 p-3"
      data-testid="assessment-history-section"
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-xs font-semibold uppercase tracking-wide text-aegis-muted">
          Assessment history (newest first)
        </p>
        <label
          htmlFor="assessment-history-source-filter"
          className="flex items-center gap-2 text-xs text-aegis-muted"
        >
          History source filter
          <select
            id="assessment-history-source-filter"
            aria-label="History source filter"
            value={assessmentSourceFilter}
            onChange={(event) => onAssessmentSourceFilterChange(event.target.value)}
            disabled={isPending}
            className="rounded border border-aegis-line bg-white px-2 py-1 font-mono text-aegis-ink"
          >
            {ASSESSMENT_SOURCE_FILTER_OPTIONS.map((option) => (
              <option key={option.value || "all"} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      </div>
      {assessmentHistory.length > 0 ? (
        <ResearchIndexHistoryChart symbol={symbol} assessments={assessmentHistory} />
      ) : null}
      {assessmentHistory.length === 0 ? (
        <p className="mt-2 font-mono text-xs text-aegis-muted">
          {assessmentSourceFilter
            ? "No assessments match this source filter."
            : "Refresh or assess to load history."}
        </p>
      ) : (
        <ul className="mt-2 space-y-1 font-mono text-xs text-aegis-ink">
          {assessmentHistory.map((row) => {
            const line = formatAssessmentHistoryRow(row);
            return (
              <li key={row.id ?? `${row.computed_at}-${line}`}>{line}</li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
