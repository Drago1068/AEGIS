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
          <dt className="text-aegis-muted">Latest lookback_start_date</dt>
          <dd className="font-mono" data-testid="evidence-latest-lookback-start-date">
            {evidenceSummary.latest_lookback_start_date ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest lookback_end_date</dt>
          <dd className="font-mono" data-testid="evidence-latest-lookback-end-date">
            {evidenceSummary.latest_lookback_end_date ?? "null"}
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
          <dt className="text-aegis-muted">Latest schema_version</dt>
          <dd className="font-mono" data-testid="evidence-latest-schema-version">
            {evidenceSummary.latest_schema_version == null
              ? "null"
              : evidenceSummary.latest_schema_version}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest computed_at</dt>
          <dd className="font-mono" data-testid="evidence-latest-computed-at">
            {evidenceSummary.latest_computed_at ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest event_time</dt>
          <dd className="font-mono" data-testid="evidence-latest-event-time">
            {evidenceSummary.latest_event_time ?? "null"}
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
          <dd className="font-mono" data-testid="evidence-latest-probability-confidence">
            {evidenceSummary.latest_probability_confidence == null
              ? "null"
              : evidenceSummary.latest_probability_confidence.toFixed(4)}
            <span className="ml-1 font-sans text-xs font-normal text-aegis-muted">
              (assessment; distinct from coverage / calibration row)
            </span>
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest assessment id</dt>
          <dd className="font-mono" data-testid="evidence-latest-assessment-id">
            {evidenceSummary.latest_assessment_id == null
              ? "null"
              : evidenceSummary.latest_assessment_id}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest outcome_label id</dt>
          <dd className="font-mono" data-testid="evidence-latest-outcome-label-id">
            {evidenceSummary.latest_outcome_label_id == null
              ? "null"
              : evidenceSummary.latest_outcome_label_id}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Most recent labeled outcome_label id</dt>
          <dd className="font-mono" data-testid="evidence-most-recent-labeled-outcome-label-id">
            {evidenceSummary.most_recent_labeled_outcome_label_id == null
              ? "null"
              : evidenceSummary.most_recent_labeled_outcome_label_id}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Most recent labeled outcome_label method_id</dt>
          <dd
            className="font-mono"
            data-testid="evidence-most-recent-labeled-outcome-label-method-id"
          >
            {evidenceSummary.most_recent_labeled_outcome_label_method_id ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Most recent labeled outcome_label method_version</dt>
          <dd
            className="font-mono"
            data-testid="evidence-most-recent-labeled-outcome-label-method-version"
          >
            {evidenceSummary.most_recent_labeled_outcome_label_method_version == null
              ? "null"
              : evidenceSummary.most_recent_labeled_outcome_label_method_version}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Most recent labeled outcome_label schema_version</dt>
          <dd
            className="font-mono"
            data-testid="evidence-most-recent-labeled-outcome-label-schema-version"
          >
            {evidenceSummary.most_recent_labeled_outcome_label_schema_version == null
              ? "null"
              : evidenceSummary.most_recent_labeled_outcome_label_schema_version}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Most recent labeled outcome_label state</dt>
          <dd
            className="font-mono"
            data-testid="evidence-most-recent-labeled-outcome-label-state"
          >
            {evidenceSummary.most_recent_labeled_outcome_label_state ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Most recent labeled outcome_label bar_source</dt>
          <dd
            className="font-mono"
            data-testid="evidence-most-recent-labeled-outcome-label-bar-source"
          >
            {evidenceSummary.most_recent_labeled_outcome_label_bar_source ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Most recent labeled outcome_label computed_at</dt>
          <dd
            className="font-mono"
            data-testid="evidence-most-recent-labeled-outcome-label-computed-at"
          >
            {evidenceSummary.most_recent_labeled_outcome_label_computed_at ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Most recent labeled outcome_label as_of_trading_date</dt>
          <dd
            className="font-mono"
            data-testid="evidence-most-recent-labeled-outcome-label-as-of-trading-date"
          >
            {evidenceSummary.most_recent_labeled_outcome_label_as_of_trading_date ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Scan-labeled freshness lag (trading days)</dt>
          <dd
            className="font-mono"
            data-testid="evidence-scan-labeled-freshness-lag-trading-days"
          >
            {evidenceSummary.scan_labeled_freshness_lag_trading_days ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest assessment is label ready</dt>
          <dd className="font-mono" data-testid="evidence-latest-assessment-is-label-ready">
            {evidenceSummary.latest_assessment_is_label_ready == null
              ? "null"
              : String(evidenceSummary.latest_assessment_is_label_ready)}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest assessment label block reason</dt>
          <dd
            className="font-mono"
            data-testid="evidence-latest-assessment-label-block-reason"
          >
            {evidenceSummary.latest_assessment_label_block_reason ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Most recent labelable as_of_trading_date</dt>
          <dd
            className="font-mono"
            data-testid="evidence-most-recent-labelable-as-of-trading-date"
          >
            {evidenceSummary.most_recent_labelable_as_of_trading_date ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Most recent unlabeled labelable as_of_trading_date</dt>
          <dd
            className="font-mono"
            data-testid="evidence-most-recent-unlabeled-labelable-as-of-trading-date"
          >
            {evidenceSummary.most_recent_unlabeled_labelable_as_of_trading_date ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Scan unlabeled label-ready count</dt>
          <dd
            className="font-mono"
            data-testid="evidence-scan-unlabeled-label-ready-count"
          >
            {evidenceSummary.scan_unlabeled_label_ready_count}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Most recent unlabeled assessment id</dt>
          <dd
            className="font-mono"
            data-testid="evidence-most-recent-unlabeled-assessment-id"
          >
            {evidenceSummary.most_recent_unlabeled_assessment_id ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Most recent unlabeled as_of_trading_date</dt>
          <dd
            className="font-mono"
            data-testid="evidence-most-recent-unlabeled-as-of-trading-date"
          >
            {evidenceSummary.most_recent_unlabeled_as_of_trading_date ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest assessment forward bar shortfall</dt>
          <dd
            className="font-mono"
            data-testid="evidence-latest-assessment-forward-bar-shortfall"
          >
            {evidenceSummary.latest_assessment_forward_bar_shortfall ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest assessment required label end date</dt>
          <dd
            className="font-mono"
            data-testid="evidence-latest-assessment-required-label-end-date"
          >
            {evidenceSummary.latest_assessment_required_label_end_date ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest assessment last available label bar date</dt>
          <dd
            className="font-mono"
            data-testid="evidence-latest-assessment-last-available-label-bar-date"
          >
            {evidenceSummary.latest_assessment_last_available_label_bar_date ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest outcome_label computed_at</dt>
          <dd className="font-mono" data-testid="evidence-latest-outcome-label-computed-at">
            {evidenceSummary.latest_outcome_label_computed_at ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest outcome_label method_id</dt>
          <dd className="font-mono" data-testid="evidence-latest-outcome-label-method-id">
            {evidenceSummary.latest_outcome_label_method_id ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest outcome_label method_version</dt>
          <dd className="font-mono" data-testid="evidence-latest-outcome-label-method-version">
            {evidenceSummary.latest_outcome_label_method_version == null
              ? "null"
              : evidenceSummary.latest_outcome_label_method_version}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest outcome_label schema_version</dt>
          <dd className="font-mono" data-testid="evidence-latest-outcome-label-schema-version">
            {evidenceSummary.latest_outcome_label_schema_version == null
              ? "null"
              : evidenceSummary.latest_outcome_label_schema_version}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest outcome_label state</dt>
          <dd className="font-mono" data-testid="evidence-latest-outcome-label-state">
            {evidenceSummary.latest_outcome_label_state ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest outcome_label bar_source</dt>
          <dd className="font-mono" data-testid="evidence-latest-outcome-label-bar-source">
            {evidenceSummary.latest_outcome_label_bar_source ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest outcome_label as_of_trading_date</dt>
          <dd className="font-mono" data-testid="evidence-latest-outcome-label-as-of-trading-date">
            {evidenceSummary.latest_outcome_label_as_of_trading_date ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest calibration id</dt>
          <dd className="font-mono" data-testid="evidence-latest-calibration-id">
            {evidenceSummary.latest_calibration_id == null
              ? "null"
              : evidenceSummary.latest_calibration_id}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest calibration horizon</dt>
          <dd className="font-mono" data-testid="evidence-latest-calibration-horizon-key">
            {evidenceSummary.latest_calibration_horizon_key ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest calibration computed_at</dt>
          <dd className="font-mono" data-testid="evidence-latest-calibration-computed-at">
            {evidenceSummary.latest_calibration_computed_at ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest calibration corpus_count</dt>
          <dd className="font-mono" data-testid="evidence-latest-calibration-corpus-count">
            {evidenceSummary.latest_calibration_corpus_count == null
              ? "null"
              : evidenceSummary.latest_calibration_corpus_count}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest calibration bucket_count</dt>
          <dd className="font-mono" data-testid="evidence-latest-calibration-bucket-count">
            {evidenceSummary.latest_calibration_bucket_count == null
              ? "null"
              : evidenceSummary.latest_calibration_bucket_count}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest calibration method_id</dt>
          <dd className="font-mono" data-testid="evidence-latest-calibration-method-id">
            {evidenceSummary.latest_calibration_method_id ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest calibration method_version</dt>
          <dd className="font-mono" data-testid="evidence-latest-calibration-method-version">
            {evidenceSummary.latest_calibration_method_version == null
              ? "null"
              : evidenceSummary.latest_calibration_method_version}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest calibration schema_version</dt>
          <dd className="font-mono" data-testid="evidence-latest-calibration-schema-version">
            {evidenceSummary.latest_calibration_schema_version == null
              ? "null"
              : evidenceSummary.latest_calibration_schema_version}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest calibration state</dt>
          <dd className="font-mono" data-testid="evidence-latest-calibration-state">
            {evidenceSummary.latest_calibration_state ?? "null"}
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest calibration probability_confidence</dt>
          <dd
            className="font-mono"
            data-testid="evidence-latest-calibration-probability-confidence"
          >
            {evidenceSummary.latest_calibration_probability_confidence == null
              ? "null"
              : evidenceSummary.latest_calibration_probability_confidence.toFixed(4)}
            <span className="ml-1 font-sans text-xs font-normal text-aegis-muted">
              (calibration row; distinct from assessment)
            </span>
          </dd>
        </div>
        <div>
          <dt className="text-aegis-muted">Latest calibration assessment_snapshot_id</dt>
          <dd
            className="font-mono"
            data-testid="evidence-latest-calibration-assessment-snapshot-id"
          >
            {evidenceSummary.latest_calibration_assessment_snapshot_id == null
              ? "null"
              : evidenceSummary.latest_calibration_assessment_snapshot_id}
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
