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

import { resolveOutcomeLabelHistoryLoadKind } from "./research-assessment-panel-helpers";
import { ResearchAssessmentActionToolbar } from "./ResearchAssessmentActionToolbar";
import { ResearchAssessmentHistorySection } from "./ResearchAssessmentHistorySection";
import { ResearchAssessmentPanelHeader } from "./ResearchAssessmentPanelHeader";
import { ResearchBackfillStatusSection } from "./ResearchBackfillStatusSection";
import { ResearchCalibrationReadinessSection } from "./ResearchCalibrationReadinessSection";
import { ResearchEvidenceSummarySection } from "./ResearchEvidenceSummarySection";
import { ResearchLatestAssessmentSection } from "./ResearchLatestAssessmentSection";
import { ResearchOutcomeLabelHistorySection } from "./ResearchOutcomeLabelHistorySection";
import { ResearchProbabilityCalibrationSection } from "./ResearchProbabilityCalibrationSection";

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
  const [evidenceSummaryEpoch, setEvidenceSummaryEpoch] = useState(0);
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
    setEvidenceSummaryEpoch((epoch) => epoch + 1);
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
      <ResearchAssessmentPanelHeader>
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
      </ResearchAssessmentPanelHeader>

      {error ? (
        <p className="mb-3 text-sm text-aegis-danger" role="alert">
          {error}
        </p>
      ) : null}

      <ResearchBackfillStatusSection
        backfillSummary={backfillSummary}
        assessmentBackfillSummary={assessmentBackfillSummary}
      />

      {evidenceSummary ? (
        <ResearchEvidenceSummarySection
          key={evidenceSummaryEpoch}
          evidenceSummary={evidenceSummary}
          isPending={isPending}
          onAssessmentSourceFilterChange={onAssessmentSourceFilterChange}
          onLoadScanLabeledLabels={onLoadScanLabeledLabels}
        />
      ) : null}

      {latest ? (
        <div className="space-y-3 text-sm">
          <ResearchLatestAssessmentSection latest={latest} />
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
          {readiness ? <ResearchCalibrationReadinessSection readiness={readiness} /> : null}
          {calibration ? (
            <ResearchProbabilityCalibrationSection
              calibration={calibration}
              calibrationHistory={calibrationHistory}
            />
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
