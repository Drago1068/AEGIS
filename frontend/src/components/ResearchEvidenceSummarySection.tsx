"use client";

import { useState } from "react";

import type { ResearchEvidenceSummary } from "@/lib/api-client";

import { sortedLabelEntries } from "./research-assessment-panel-helpers";

export type ResearchEvidenceSummarySectionProps = {
  evidenceSummary: ResearchEvidenceSummary;
  isPending: boolean;
  onAssessmentSourceFilterChange: (value: string) => void;
  onLoadScanLabeledLabels: () => void;
};

export function ResearchEvidenceSummarySection({
  evidenceSummary,
  isPending,
  onAssessmentSourceFilterChange,
  onLoadScanLabeledLabels,
}: ResearchEvidenceSummarySectionProps) {
  const [expandedHorizonKey, setExpandedHorizonKey] = useState<string | null>(null);

  return (
    <div
      className="mb-4 rounded border border-aegis-line bg-white/60 p-3 text-sm"
      data-testid="evidence-summary-section"
    >
      <p className="text-xs font-semibold uppercase tracking-wide text-aegis-muted">
        Evidence summary (research-only — not advice)
      </p>
      <dl className="mt-2 grid gap-2 sm:grid-cols-2">
        <div>
          <dt className="text-aegis-muted">State</dt>
          <dd className="font-mono">{evidenceSummary.state}</dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Readiness</dt>
          <dd className="font-mono">{evidenceSummary.calibration_readiness.status}</dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Calibration corpus (readiness)</dt>
          <dd className="font-mono">
            {evidenceSummary.calibration_readiness.corpus_count} / min{" "}
            {evidenceSummary.calibration_readiness.min_corpus}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Calibration bucket (readiness)</dt>
          <dd className="font-mono">
            {evidenceSummary.calibration_readiness.bucket_count} / min{" "}
            {evidenceSummary.calibration_readiness.min_bucket}
          </dd>
        </div>
        {evidenceSummary.calibration_readiness.by_horizon &&
        evidenceSummary.calibration_readiness.by_horizon.length > 0 ? (
          <div className="sm:col-span-2" data-testid="evidence-readiness-by-horizon">
            <dt className="text-aegis-muted">Readiness by horizon</dt>
            <dd>
              <ul className="mt-1 space-y-1 text-xs text-aegis-muted">
                {evidenceSummary.calibration_readiness.by_horizon.map((row) => {
                  const expanded = expandedHorizonKey === row.outcome_horizon_key;
                  return (
                    <li key={row.outcome_horizon_key}>
                      <button
                        type="button"
                        className="w-full text-left font-mono underline-offset-2 hover:underline"
                        aria-expanded={expanded}
                        data-testid={`evidence-horizon-${row.outcome_horizon_key}`}
                        onClick={() =>
                          setExpandedHorizonKey(expanded ? null : row.outcome_horizon_key)
                        }
                      >
                        {row.outcome_horizon_key}: {row.status} (corpus=
                        {row.corpus_count}, bucket={row.bucket_count})
                      </button>
                      {expanded ? (
                        <p
                          className="mt-1 pl-2 text-xs text-aegis-muted"
                          data-testid={`evidence-horizon-detail-${row.outcome_horizon_key}`}
                        >
                          {row.detail || "(no detail)"}
                        </p>
                      ) : null}
                    </li>
                  );
                })}
              </ul>
            </dd>
          </div>
        ) : null}
        <div>
          <dt className="text-aegis-muted">Assessments (≤100)</dt>
          <dd className="font-mono">{evidenceSummary.assessment_count}</dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Labeled (scanned)</dt>
          <dd className="font-mono" data-testid="evidence-labeled-assessment-count">
            {evidenceSummary.labeled_assessment_count}
            <span className="ml-1 font-sans text-xs font-normal text-aegis-muted">
              of {evidenceSummary.assessment_count}
            </span>
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Unlabeled (scanned)</dt>
          <dd className="font-mono" data-testid="evidence-unlabeled-assessment-count">
            {evidenceSummary.unlabeled_assessment_count}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Labels / calibrations (latest id)</dt>
          <dd className="font-mono">
            {evidenceSummary.outcome_label_count} / {evidenceSummary.calibration_count}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest component source</dt>
          <dd className="font-mono">
            {evidenceSummary.latest_component_source ?? "null"}
            {evidenceSummary.latest_component_source === "mixed"
              ? " (cross-source fill)"
              : null}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Resolved label bar source</dt>
          <dd className="font-mono">
            {evidenceSummary.latest_resolved_label_bar_source ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Mixed-source assessments (scanned)</dt>
          <dd className="font-mono">
            {evidenceSummary.mixed_component_source_assessment_count > 0 ? (
              <button
                type="button"
                onClick={() => {
                  onAssessmentSourceFilterChange("mixed");
                  const history = document.getElementById("assessment-history");
                  if (history && typeof history.scrollIntoView === "function") {
                    history.scrollIntoView({ behavior: "smooth", block: "nearest" });
                  }
                }}
                disabled={isPending}
                className="underline decoration-aegis-line underline-offset-2 hover:text-aegis-ink disabled:opacity-60"
                aria-label="Filter assessment history to mixed component source"
              >
                {evidenceSummary.mixed_component_source_assessment_count}
                <span className="ml-1 font-sans text-xs font-normal text-aegis-muted">
                  (show in history)
                </span>
              </button>
            ) : (
              evidenceSummary.mixed_component_source_assessment_count
            )}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Mixed labeled (scanned)</dt>
          <dd className="font-mono">
            {evidenceSummary.mixed_labeled_assessment_count}
            <span className="ml-1 font-sans text-xs font-normal text-aegis-muted">
              of {evidenceSummary.mixed_component_source_assessment_count} mixed
            </span>
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Mixed unlabeled (scanned)</dt>
          <dd className="font-mono">{evidenceSummary.mixed_unlabeled_assessment_count}</dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest mixed label bar source</dt>
          <dd className="font-mono">
            {evidenceSummary.latest_mixed_label_bar_source ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest research_index</dt>
          <dd className="font-mono" data-testid="evidence-latest-research-index">
            {evidenceSummary.latest_research_index == null
              ? "null"
              : evidenceSummary.latest_research_index.toFixed(4)}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest as_of_trading_date</dt>
          <dd className="font-mono" data-testid="evidence-latest-as-of-trading-date">
            {evidenceSummary.latest_as_of_trading_date ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest bar_count</dt>
          <dd className="font-mono" data-testid="evidence-latest-bar-count">
            {evidenceSummary.latest_bar_count == null
              ? "null"
              : evidenceSummary.latest_bar_count}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest input_source</dt>
          <dd className="font-mono" data-testid="evidence-latest-input-source">
            {evidenceSummary.latest_input_source ?? "null"}
            <span className="ml-1 font-sans text-xs font-normal text-aegis-muted">
              (distinct from component source)
            </span>
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest method_id</dt>
          <dd className="font-mono" data-testid="evidence-latest-method-id">
            {evidenceSummary.latest_method_id ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest method_version</dt>
          <dd className="font-mono" data-testid="evidence-latest-method-version">
            {evidenceSummary.latest_method_version == null
              ? "null"
              : evidenceSummary.latest_method_version}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest coverage_confidence</dt>
          <dd className="font-mono" data-testid="evidence-latest-coverage-confidence">
            {evidenceSummary.latest_coverage_confidence == null
              ? "null"
              : evidenceSummary.latest_coverage_confidence.toFixed(4)}
            <span className="ml-1 font-sans text-xs font-normal text-aegis-muted">
              (distinct from probability)
            </span>
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest probability_confidence</dt>
          <dd className="font-mono">
            {evidenceSummary.latest_calibration == null
              ? "null"
              : evidenceSummary.latest_calibration.probability_confidence.toFixed(4)}
          </dd>
        </div>
        {evidenceSummary.latest_outcome_label == null ? (
          <div>
            <dt className="text-aegis-muted">Latest outcome labels</dt>
            <dd className="font-mono">null</dd>
          </div>
        ) : (
          sortedLabelEntries(evidenceSummary.latest_outcome_label.labels).map(
            ([key, value]) => {
              const end = evidenceSummary.latest_outcome_label?.label_end_dates?.[key];
              return (
                <div key={key}>
                  <dt className="text-aegis-muted">Latest {key}</dt>
                  <dd className="font-mono">
                    {value.toFixed(4)}
                    {typeof end === "string" && end.length > 0 ? ` · end ${end}` : null}
                  </dd>
                </div>
              );
            },
          )
        )}
        {evidenceSummary.most_recent_labeled_outcome_label != null &&
        (evidenceSummary.latest_outcome_label == null ||
          evidenceSummary.most_recent_labeled_assessment_id !==
            evidenceSummary.latest_assessment?.id) ? (
          <>
            <div>
              <dt className="text-aegis-muted">Most recent labeled assessment id</dt>
              <dd className="font-mono" data-testid="most-recent-labeled-assessment-id">
                {evidenceSummary.most_recent_labeled_assessment_id ?? "null"}
              </dd>
            </div>
            {sortedLabelEntries(
              evidenceSummary.most_recent_labeled_outcome_label.labels,
            ).map(([key, value]) => {
              const end =
                evidenceSummary.most_recent_labeled_outcome_label?.label_end_dates?.[key];
              return (
                <div key={`scan-${key}`}>
                  <dt className="text-aegis-muted">Scan-labeled {key}</dt>
                  <dd className="font-mono">
                    {value.toFixed(4)}
                    {typeof end === "string" && end.length > 0 ? ` · end ${end}` : null}
                  </dd>
                </div>
              );
            })}
            <div className="sm:col-span-2">
              <button
                type="button"
                className="text-sm underline-offset-2 hover:underline"
                disabled={isPending || evidenceSummary.most_recent_labeled_assessment_id == null}
                data-testid="load-scan-labeled-labels"
                onClick={onLoadScanLabeledLabels}
              >
                Load labels for assessment{" "}
                {evidenceSummary.most_recent_labeled_assessment_id}
              </button>
            </div>
          </>
        ) : null}
      </dl>
      <p className="mt-2 text-xs text-aegis-muted">{evidenceSummary.detail}</p>
    </div>
  );
}
