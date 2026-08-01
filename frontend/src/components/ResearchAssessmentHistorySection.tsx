"use client";

import { useState } from "react";

import type { ResearchAssessment } from "@/lib/api-client";

import { CoverageConfidenceHistoryChart } from "./CoverageConfidenceHistoryChart";
import { ResearchIndexHistoryChart } from "./ResearchIndexHistoryChart";
import {
  ASSESSMENT_SOURCE_FILTER_OPTIONS,
  distinctAsOfAssessments,
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
  const [showAllAsOf, setShowAllAsOf] = useState(false);
  const distinctRows = distinctAsOfAssessments(assessmentHistory);
  const visibleRows = showAllAsOf ? assessmentHistory : distinctRows;
  const hiddenDuplicateCount = assessmentHistory.length - distinctRows.length;

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
        <div className="flex flex-wrap items-center gap-3">
          {assessmentHistory.length > 0 ? (
            <label
              htmlFor="assessment-history-show-all-as-of"
              className="flex items-center gap-2 text-xs text-aegis-muted"
            >
              <input
                id="assessment-history-show-all-as-of"
                type="checkbox"
                checked={showAllAsOf}
                onChange={(event) => setShowAllAsOf(event.target.checked)}
                disabled={isPending}
                data-testid="assessment-history-show-all-as-of"
                aria-label="Show all assessment rows including duplicate as_of dates"
              />
              Show all rows
              <span
                className="font-mono text-aegis-ink"
                data-testid="assessment-history-as-of-counts"
              >
                ({distinctRows.length} distinct as_of
                {hiddenDuplicateCount > 0 && !showAllAsOf
                  ? ` · ${hiddenDuplicateCount} hidden`
                  : ` · ${assessmentHistory.length} total`}
                )
              </span>
            </label>
          ) : null}
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
      </div>
      {assessmentHistory.length > 0 ? (
        <>
          <ResearchIndexHistoryChart symbol={symbol} assessments={assessmentHistory} />
          <CoverageConfidenceHistoryChart
            symbol={symbol}
            assessments={assessmentHistory}
          />
        </>
      ) : null}
      {assessmentHistory.length === 0 ? (
        <p className="mt-2 font-mono text-xs text-aegis-muted">
          {assessmentSourceFilter
            ? "No assessments match this source filter."
            : "Refresh or assess to load history."}
        </p>
      ) : (
        <ul
          className="mt-2 space-y-1 font-mono text-xs text-aegis-ink"
          data-testid="assessment-history-list"
          data-history-mode={showAllAsOf ? "all" : "distinct_as_of"}
        >
          {visibleRows.map((row) => {
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
