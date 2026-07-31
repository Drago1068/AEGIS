"use client";

import { useState, useTransition } from "react";

import {
  ApiClientError,
  AssessmentBackfillResponse,
  CalibrationReadiness,
  OutcomeLabel,
  OutcomeLabelBackfillResponse,
  ProbabilityCalibration,
  ResearchAssessment,
  ResearchEvidenceSummary,
  backfillOutcomeLabels,
  backfillResearchAssessments,
  createOutcomeLabels,
  createProbabilityCalibration,
  createResearchAssessment,
  downloadCalibrationReadiness,
  downloadOutcomeLabels,
  downloadProbabilityCalibrations,
  downloadResearchAssessments,
  downloadResearchEvidenceSummary,
  getApiBaseUrl,
  getCalibrationReadiness,
  getLatestResearchAssessment,
  getResearchEvidenceSummary,
  listOutcomeLabels,
  listProbabilityCalibrations,
  listResearchAssessments,
} from "@/lib/api-client";

import {
  resolveOutcomeLabelHistoryLoadKind,
  sortedLabelEntries,
} from "./research-assessment-panel-helpers";
import { ResearchAssessmentActionToolbar } from "./ResearchAssessmentActionToolbar";
import { ResearchAssessmentHistorySection } from "./ResearchAssessmentHistorySection";
import { ResearchOutcomeLabelHistorySection } from "./ResearchOutcomeLabelHistorySection";

type ResearchAssessmentPanelProps = {
  symbol: string;
  initialLatest: ResearchAssessment | null;
};

function formatAssessmentError(err: unknown): string {
  if (!(err instanceof ApiClientError)) {
    return "Research assessment request failed.";
  }
  if (err.status === 422 && err.body && typeof err.body === "object") {
    const detail = (err.body as { detail?: unknown }).detail;
    if (detail && typeof detail === "object") {
      const reason = (detail as { reason?: unknown }).reason;
      const message = (detail as { message?: unknown }).message;
      if (typeof reason === "string" && typeof message === "string") {
        return `Unavailable (${reason}): ${message}`;
      }
    }
  }
  return err.message;
}

export function ResearchAssessmentPanel({
  symbol,
  initialLatest,
}: ResearchAssessmentPanelProps) {
  const [latest, setLatest] = useState<ResearchAssessment | null>(initialLatest);
  const [assessmentHistory, setAssessmentHistory] = useState<ResearchAssessment[]>([]);
  const [outcomeLabel, setOutcomeLabel] = useState<OutcomeLabel | null>(null);
  const [outcomeLabelHistory, setOutcomeLabelHistory] = useState<OutcomeLabel[]>([]);
  const [outcomeLabelHistoryAssessmentId, setOutcomeLabelHistoryAssessmentId] = useState<
    number | null
  >(null);
  const [outcomeLabelHistoryLoadKind, setOutcomeLabelHistoryLoadKind] = useState<
    "latest" | "scan_labeled" | null
  >(null);
  const [readiness, setReadiness] = useState<CalibrationReadiness | null>(null);
  const [calibration, setCalibration] = useState<ProbabilityCalibration | null>(null);
  const [calibrationHistory, setCalibrationHistory] = useState<ProbabilityCalibration[]>(
    [],
  );
  const [evidenceSummary, setEvidenceSummary] = useState<ResearchEvidenceSummary | null>(
    null,
  );
  const [backfillSummary, setBackfillSummary] = useState<OutcomeLabelBackfillResponse | null>(
    null,
  );
  const [assessmentBackfillSummary, setAssessmentBackfillSummary] =
    useState<AssessmentBackfillResponse | null>(null);
  const [assessmentSourceFilter, setAssessmentSourceFilter] = useState("");
  const [expandedHorizonKey, setExpandedHorizonKey] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const baseUrl = getApiBaseUrl();

  async function loadAssessmentHistory(componentSource?: string) {
    const source = componentSource ?? assessmentSourceFilter;
    const rows = await listResearchAssessments(baseUrl, symbol, 20, {
      componentSource: source || null,
    });
    setAssessmentHistory(rows);
  }

  async function loadReadiness() {
    const next = await getCalibrationReadiness(baseUrl, symbol);
    setReadiness(next);
  }

  async function loadEvidenceSummary() {
    const next = await getResearchEvidenceSummary(baseUrl, symbol);
    setEvidenceSummary(next);
    setExpandedHorizonKey(null);
  }

  async function loadOutcomeLabelHistory(
    assessmentId: number,
    loadKind: "latest" | "scan_labeled" = "latest",
  ) {
    const rows = await listOutcomeLabels(baseUrl, symbol, assessmentId, 20);
    setOutcomeLabelHistory(rows);
    setOutcomeLabel(rows[0] ?? null);
    setOutcomeLabelHistoryAssessmentId(assessmentId);
    setOutcomeLabelHistoryLoadKind(loadKind);
  }

  async function loadCalibrationHistory(assessmentId: number) {
    const rows = await listProbabilityCalibrations(baseUrl, symbol, assessmentId, 20);
    setCalibrationHistory(rows);
    const newest = rows[0] ?? null;
    setCalibration(newest);
    if (newest != null) {
      setLatest((current) =>
        current == null
          ? current
          : { ...current, probability_confidence: newest.probability_confidence },
      );
    }
  }

  function onAssess() {
    startTransition(async () => {
      setError(null);
      try {
        const snapshot = await createResearchAssessment(baseUrl, symbol);
        setLatest(snapshot);
        setOutcomeLabel(null);
        setOutcomeLabelHistory([]);
        setOutcomeLabelHistoryAssessmentId(null);
        setOutcomeLabelHistoryLoadKind(null);
        setCalibration(null);
        setCalibrationHistory([]);
        setEvidenceSummary(null);
        await loadAssessmentHistory();
        await loadReadiness();
        if (snapshot.id != null) {
          await loadOutcomeLabelHistory(snapshot.id, "latest");
          await loadCalibrationHistory(snapshot.id);
        }
        await loadEvidenceSummary();
      } catch (err) {
        setError(formatAssessmentError(err));
      }
    });
  }

  function onRefreshLatest() {
    startTransition(async () => {
      setError(null);
      try {
        const snapshot = await getLatestResearchAssessment(baseUrl, symbol);
        setLatest(snapshot);
        setOutcomeLabel(null);
        setOutcomeLabelHistory([]);
        setOutcomeLabelHistoryAssessmentId(null);
        setOutcomeLabelHistoryLoadKind(null);
        setCalibration(null);
        setCalibrationHistory([]);
        setEvidenceSummary(null);
        await loadAssessmentHistory();
        if (snapshot.id != null) {
          await loadOutcomeLabelHistory(snapshot.id, "latest");
          await loadCalibrationHistory(snapshot.id);
        }
        await loadReadiness();
        await loadEvidenceSummary();
      } catch (err) {
        if (err instanceof ApiClientError && err.status === 404) {
          setLatest(null);
          setAssessmentHistory([]);
          setOutcomeLabel(null);
          setOutcomeLabelHistory([]);
          setOutcomeLabelHistoryAssessmentId(null);
          setOutcomeLabelHistoryLoadKind(null);
          setReadiness(null);
          setCalibration(null);
          setCalibrationHistory([]);
          setEvidenceSummary(null);
          setError(null);
          try {
            await loadEvidenceSummary();
          } catch {
            // empty summary optional when symbol has no assessments
          }
          return;
        }
        setError(formatAssessmentError(err));
      }
    });
  }

  const activeOutcomeLabelAssessmentId =
    outcomeLabelHistoryAssessmentId ?? latest?.id ?? null;

  function onComputeOutcomeLabels() {
    const assessmentId = activeOutcomeLabelAssessmentId;
    if (assessmentId == null) {
      return;
    }
    const loadKind = resolveOutcomeLabelHistoryLoadKind(
      assessmentId,
      outcomeLabelHistoryLoadKind,
      latest?.id,
    );
    startTransition(async () => {
      setError(null);
      try {
        await createOutcomeLabels(baseUrl, symbol, assessmentId);
        await loadOutcomeLabelHistory(assessmentId, loadKind);
        await loadReadiness();
        await loadEvidenceSummary();
      } catch (err) {
        setError(formatAssessmentError(err));
      }
    });
  }

  function onBackfillOutcomeLabels() {
    startTransition(async () => {
      setError(null);
      try {
        const summary = await backfillOutcomeLabels(baseUrl, symbol, 100);
        setBackfillSummary(summary);
        const assessmentId = activeOutcomeLabelAssessmentId;
        if (assessmentId != null) {
          const loadKind = resolveOutcomeLabelHistoryLoadKind(
            assessmentId,
            outcomeLabelHistoryLoadKind,
            latest?.id,
          );
          await loadOutcomeLabelHistory(assessmentId, loadKind);
        }
        await loadReadiness();
        await loadEvidenceSummary();
      } catch (err) {
        setError(formatAssessmentError(err));
      }
    });
  }

  function onBackfillAssessments() {
    startTransition(async () => {
      setError(null);
      try {
        const summary = await backfillResearchAssessments(baseUrl, symbol, 20);
        setAssessmentBackfillSummary(summary);
        await loadAssessmentHistory();
        const trackedLabelAssessmentId = outcomeLabelHistoryAssessmentId;
        const trackedLoadKind = outcomeLabelHistoryLoadKind;
        try {
          const nextLatest = await getLatestResearchAssessment(baseUrl, symbol);
          setLatest(nextLatest);
          const labelAssessmentId = trackedLabelAssessmentId ?? nextLatest.id ?? null;
          if (labelAssessmentId != null) {
            const loadKind = resolveOutcomeLabelHistoryLoadKind(
              labelAssessmentId,
              trackedLoadKind,
              nextLatest.id,
            );
            await loadOutcomeLabelHistory(labelAssessmentId, loadKind);
          }
          if (nextLatest.id != null) {
            await loadCalibrationHistory(nextLatest.id);
          }
        } catch (err) {
          if (!(err instanceof ApiClientError && err.status === 404)) {
            throw err;
          }
        }
        await loadReadiness();
        await loadEvidenceSummary();
      } catch (err) {
        setError(formatAssessmentError(err));
      }
    });
  }

  function onDownloadOutcomeLabels() {
    const assessmentId = activeOutcomeLabelAssessmentId;
    if (assessmentId == null) {
      return;
    }
    startTransition(async () => {
      setError(null);
      try {
        await downloadOutcomeLabels(baseUrl, symbol, assessmentId, 20);
      } catch (err) {
        setError(formatAssessmentError(err));
      }
    });
  }

  function onDownloadCalibrations() {
    if (latest?.id == null) {
      return;
    }
    startTransition(async () => {
      setError(null);
      try {
        await downloadProbabilityCalibrations(baseUrl, symbol, latest.id as number, 20);
      } catch (err) {
        setError(formatAssessmentError(err));
      }
    });
  }

  function onComputeCalibration() {
    if (latest?.id == null || readiness?.status !== "ready") {
      return;
    }
    startTransition(async () => {
      setError(null);
      try {
        const horizons =
          readiness.by_horizon && readiness.by_horizon.length > 0
            ? readiness.by_horizon
                .filter((row) => row.status === "ready")
                .map((row) => row.outcome_horizon_key)
            : ["forward_return_5"];
        const targets = horizons.length > 0 ? horizons : ["forward_return_5"];
        for (const horizon of targets) {
          await createProbabilityCalibration(baseUrl, symbol, latest.id as number, horizon);
        }
        await loadCalibrationHistory(latest.id as number);
        await loadReadiness();
        await loadEvidenceSummary();
      } catch (err) {
        setError(formatAssessmentError(err));
      }
    });
  }

  function onRefreshEvidenceSummary() {
    startTransition(async () => {
      setError(null);
      try {
        await loadEvidenceSummary();
      } catch (err) {
        setError(formatAssessmentError(err));
      }
    });
  }

  function onLoadScanLabeledLabels() {
    const assessmentId = evidenceSummary?.most_recent_labeled_assessment_id;
    if (assessmentId == null) {
      return;
    }
    startTransition(async () => {
      setError(null);
      try {
        await loadOutcomeLabelHistory(assessmentId, "scan_labeled");
      } catch (err) {
        setError(formatAssessmentError(err));
      }
    });
  }

  function onLoadLatestLabels() {
    if (latest?.id == null) {
      return;
    }
    startTransition(async () => {
      setError(null);
      try {
        await loadOutcomeLabelHistory(latest.id as number, "latest");
      } catch (err) {
        setError(formatAssessmentError(err));
      }
    });
  }

  function onDownloadEvidenceSummary() {
    startTransition(async () => {
      setError(null);
      try {
        await downloadResearchEvidenceSummary(baseUrl, symbol);
      } catch (err) {
        setError(formatAssessmentError(err));
      }
    });
  }

  function onDownloadAssessments() {
    startTransition(async () => {
      setError(null);
      try {
        await downloadResearchAssessments(baseUrl, symbol, 20, {
          componentSource: assessmentSourceFilter || null,
        });
      } catch (err) {
        setError(formatAssessmentError(err));
      }
    });
  }

  function onAssessmentSourceFilterChange(next: string) {
    setAssessmentSourceFilter(next);
    startTransition(async () => {
      setError(null);
      try {
        await loadAssessmentHistory(next);
      } catch (err) {
        setError(formatAssessmentError(err));
      }
    });
  }

  function onRefreshReadiness() {
    startTransition(async () => {
      setError(null);
      try {
        await loadReadiness();
      } catch (err) {
        setError(formatAssessmentError(err));
      }
    });
  }

  function onDownloadReadiness() {
    startTransition(async () => {
      setError(null);
      try {
        await downloadCalibrationReadiness(baseUrl, symbol);
      } catch (err) {
        setError(formatAssessmentError(err));
      }
    });
  }

  return (
    <section className="rounded-lg border border-aegis-line bg-aegis-panel p-5 shadow-sm">
      <header className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-1">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-aegis-warn">
            Research only
          </p>
          <h2 className="text-lg font-semibold tracking-tight text-aegis-ink">
            Research assessment
          </h2>
          <p className="text-sm text-aegis-muted">
            Research heuristic from stored primary daily bars (on-demand or after a successful
            ingest when configured). Not a probability, signal, or recommendation. Values come
            from the API only — refresh latest to see post-ingest snapshots.
          </p>
        </div>
        <ResearchAssessmentActionToolbar
          isPending={isPending}
          activeOutcomeLabelAssessmentId={activeOutcomeLabelAssessmentId}
          outcomeLabelHistoryLoadKind={outcomeLabelHistoryLoadKind}
          outcomeLabelHistoryAssessmentId={outcomeLabelHistoryAssessmentId}
          latestId={latest?.id ?? null}
          readinessStatus={readiness?.status}
          onRefreshLatest={onRefreshLatest}
          onRefreshReadiness={onRefreshReadiness}
          onDownloadReadiness={onDownloadReadiness}
          onRefreshEvidenceSummary={onRefreshEvidenceSummary}
          onDownloadEvidenceSummary={onDownloadEvidenceSummary}
          onDownloadAssessments={onDownloadAssessments}
          onBackfillAssessments={onBackfillAssessments}
          onComputeOutcomeLabels={onComputeOutcomeLabels}
          onBackfillOutcomeLabels={onBackfillOutcomeLabels}
          onDownloadOutcomeLabels={onDownloadOutcomeLabels}
          onComputeCalibration={onComputeCalibration}
          onDownloadCalibrations={onDownloadCalibrations}
          onAssess={onAssess}
        />
      </header>

      {error ? (
        <p className="mb-3 text-sm text-aegis-danger" role="alert">
          {error}
        </p>
      ) : null}

      {backfillSummary ? (
        <p className="mb-3 text-sm text-aegis-muted" data-testid="outcome-label-backfill-summary">
          Backfill (research-only): attempted={backfillSummary.assessment_count}, labeled=
          {backfillSummary.persisted_count}, skipped={backfillSummary.skipped_count}
        </p>
      ) : null}

      {assessmentBackfillSummary ? (
        <p
          className="mb-3 text-sm text-aegis-muted"
          data-testid="assessment-backfill-summary"
        >
          Assessment backfill (research-only): candidates=
          {assessmentBackfillSummary.candidate_count}, persisted=
          {assessmentBackfillSummary.persisted_count}, skipped=
          {assessmentBackfillSummary.skipped_count}
        </p>
      ) : null}

      {evidenceSummary ? (
        <div className="mb-4 rounded border border-aegis-line bg-white/60 p-3 text-sm">
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
                              setExpandedHorizonKey(
                                expanded ? null : row.outcome_horizon_key,
                              )
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
              <dd className="font-mono">
                {evidenceSummary.mixed_unlabeled_assessment_count}
              </dd>
            </div>
            <div>
              <dt className="text-aegis-muted">Latest mixed label bar source</dt>
              <dd className="font-mono">
                {evidenceSummary.latest_mixed_label_bar_source ?? "null"}
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
                  const end =
                    evidenceSummary.latest_outcome_label?.label_end_dates?.[key];
                  return (
                    <div key={key}>
                      <dt className="text-aegis-muted">Latest {key}</dt>
                      <dd className="font-mono">
                        {value.toFixed(4)}
                        {typeof end === "string" && end.length > 0
                          ? ` · end ${end}`
                          : null}
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
                    evidenceSummary.most_recent_labeled_outcome_label?.label_end_dates?.[
                      key
                    ];
                  return (
                    <div key={`scan-${key}`}>
                      <dt className="text-aegis-muted">Scan-labeled {key}</dt>
                      <dd className="font-mono">
                        {value.toFixed(4)}
                        {typeof end === "string" && end.length > 0
                          ? ` · end ${end}`
                          : null}
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
      ) : null}

      {latest ? (
        <div className="space-y-3 text-sm">
          <p className="font-semibold uppercase tracking-wide text-aegis-warn">
            State: {latest.state.replaceAll("_", " ")}
          </p>
          <dl className="grid gap-2 sm:grid-cols-2">
            <div>
              <dt className="text-aegis-muted">Method</dt>
              <dd className="font-mono">
                {latest.method_id} v{latest.method_version}
              </dd>
            </div>
            <div>
              <dt className="text-aegis-muted">As-of trading date</dt>
              <dd className="font-mono">{latest.as_of_trading_date}</dd>
            </div>
            <div>
              <dt className="text-aegis-muted">Coverage confidence</dt>
              <dd className="font-mono">{latest.coverage_confidence.toFixed(4)}</dd>
            </div>
            <div>
              <dt className="text-aegis-muted">Probability confidence</dt>
              <dd className="font-mono">
                {latest.probability_confidence === null
                  ? "null (not calibrated)"
                  : `${latest.probability_confidence.toFixed(4)} (calibrated research-only)`}
              </dd>
            </div>
            <div>
              <dt className="text-aegis-muted">total_return_20</dt>
              <dd className="font-mono">{String(latest.components.total_return_20)}</dd>
            </div>
            <div>
              <dt className="text-aegis-muted">realized_vol_20</dt>
              <dd className="font-mono">{String(latest.components.realized_vol_20)}</dd>
            </div>
            <div>
              <dt className="text-aegis-muted">research_index</dt>
              <dd className="font-mono">{String(latest.components.research_index)}</dd>
            </div>
            <div>
              <dt className="text-aegis-muted">Lookback</dt>
              <dd className="font-mono">
                {latest.lookback_start_date} → {latest.lookback_end_date} (
                {latest.bar_count} bars)
              </dd>
            </div>
            {typeof latest.components.component_source === "string" ? (
              <div>
                <dt className="text-aegis-muted">Component source</dt>
                <dd className="font-mono">
                  {latest.components.component_source}
                  {latest.components.component_source === "mixed"
                    ? " (cross-source fill — research only)"
                    : null}
                </dd>
              </div>
            ) : null}
            {typeof latest.components.source_availability_factor === "number" ? (
              <div>
                <dt className="text-aegis-muted">Source availability factor</dt>
                <dd className="font-mono">
                  {latest.components.source_availability_factor.toFixed(4)}
                </dd>
              </div>
            ) : null}
            {typeof latest.components.source_agreement_factor === "number" ? (
              <div>
                <dt className="text-aegis-muted">Source agreement factor</dt>
                <dd className="font-mono">
                  {latest.components.source_agreement_factor.toFixed(4)}
                  {typeof latest.components.agreeing_dates === "number" &&
                  typeof latest.components.comparable_dates === "number"
                    ? ` (${latest.components.agreeing_dates}/${latest.components.comparable_dates} comparable)`
                    : null}
                </dd>
              </div>
            ) : null}
          </dl>
          <p className="text-xs text-aegis-muted">
            Computed at {latest.computed_at} from source {latest.input_source}. Research
            only — not actionable.
          </p>
          <ResearchAssessmentHistorySection
            assessmentHistory={assessmentHistory}
            assessmentSourceFilter={assessmentSourceFilter}
            isPending={isPending}
            onAssessmentSourceFilterChange={onAssessmentSourceFilterChange}
          />
          <ResearchOutcomeLabelHistorySection
            outcomeLabel={outcomeLabel}
            outcomeLabelHistory={outcomeLabelHistory}
            outcomeLabelHistoryAssessmentId={outcomeLabelHistoryAssessmentId}
            outcomeLabelHistoryLoadKind={outcomeLabelHistoryLoadKind}
            latestId={latest?.id ?? null}
            isPending={isPending}
            onLoadLatestLabels={onLoadLatestLabels}
          />
          {readiness ? (
            <div className="rounded border border-aegis-line bg-white/60 p-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-aegis-muted">
                Calibration readiness (diagnostics only — not advice)
              </p>
              <dl className="mt-2 grid gap-2 sm:grid-cols-2">
                <div>
                  <dt className="text-aegis-muted">Status</dt>
                  <dd className="font-mono">{readiness.status}</dd>
                </div>
                <div>
                  <dt className="text-aegis-muted">Method</dt>
                  <dd className="font-mono">{readiness.calibration_method_id}</dd>
                </div>
                <div>
                  <dt className="text-aegis-muted">Primary horizon</dt>
                  <dd className="font-mono">
                    {readiness.outcome_horizon_key ?? "forward_return_5"}
                  </dd>
                </div>
                <div>
                  <dt className="text-aegis-muted">Labeled corpus</dt>
                  <dd className="font-mono">
                    {readiness.corpus_count} / min {readiness.min_corpus}
                  </dd>
                </div>
                <div>
                  <dt className="text-aegis-muted">Similarity bucket</dt>
                  <dd className="font-mono">
                    {readiness.bucket_count} / min {readiness.min_bucket} (±
                    {readiness.index_bucket_width})
                  </dd>
                </div>
              </dl>
              {readiness.by_horizon && readiness.by_horizon.length > 0 ? (
                <ul className="mt-2 space-y-1 text-xs text-aegis-muted">
                  {readiness.by_horizon.map((row) => (
                    <li key={row.outcome_horizon_key} className="font-mono">
                      {row.outcome_horizon_key}: {row.status} (corpus={row.corpus_count}, bucket=
                      {row.bucket_count})
                    </li>
                  ))}
                </ul>
              ) : null}
              <p className="mt-2 text-xs text-aegis-muted">{readiness.detail}</p>
            </div>
          ) : null}
          {calibration ? (
            <div className="rounded border border-aegis-line bg-white/60 p-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-aegis-muted">
                Probability calibration (research-only — not advice)
              </p>
              <dl className="mt-2 grid gap-2 sm:grid-cols-2">
                <div>
                  <dt className="text-aegis-muted">probability_confidence</dt>
                  <dd className="font-mono">{calibration.probability_confidence.toFixed(4)}</dd>
                </div>
                <div>
                  <dt className="text-aegis-muted">Method</dt>
                  <dd className="font-mono">
                    {calibration.calibration_method_id} v{calibration.calibration_method_version}
                  </dd>
                </div>
                <div>
                  <dt className="text-aegis-muted">Horizon</dt>
                  <dd className="font-mono">
                    {calibration.outcome_horizon_key ?? "forward_return_5"}
                  </dd>
                </div>
                <div>
                  <dt className="text-aegis-muted">Corpus / bucket</dt>
                  <dd className="font-mono">
                    {calibration.corpus_count} / {calibration.bucket_count}
                  </dd>
                </div>
                <div>
                  <dt className="text-aegis-muted">Computed at</dt>
                  <dd className="font-mono">{calibration.computed_at}</dd>
                </div>
              </dl>
              {calibrationHistory.length > 1 ? (
                <div className="mt-3 border-t border-aegis-line pt-3">
                  <p className="text-xs font-semibold uppercase tracking-wide text-aegis-muted">
                    Calibration history (newest first)
                  </p>
                  <ul className="mt-2 space-y-1 font-mono text-xs text-aegis-ink">
                    {calibrationHistory.map((row) => (
                      <li
                        key={
                          row.id ??
                          `${row.computed_at}-${row.outcome_horizon_key}-${row.probability_confidence}`
                        }
                      >
                        {row.computed_at} · {row.outcome_horizon_key ?? "forward_return_5"} · p=
                        {row.probability_confidence.toFixed(4)} · corpus=
                        {row.corpus_count}/{row.bucket_count}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </div>
          ) : null}
        </div>
      ) : !error ? (
        <p className="text-sm text-aegis-muted">
          No research assessment stored yet for {symbol}. Run an assessment to append one.
        </p>
      ) : null}
    </section>
  );
}
