"use client";

import type { ReactNode } from "react";

import {
  formatCalibrationActionAriaLabel,
  formatCalibrationActionIdChip,
  formatOutcomeLabelActionAriaLabel,
  formatOutcomeLabelActionIdChip,
  formatOutcomeLabelBackfillAriaLabel,
  type OutcomeLabelHistoryLoadKind,
} from "./research-assessment-panel-helpers";

const BUTTON_CLASS =
  "rounded border border-aegis-line bg-white px-3 py-2 text-sm font-medium text-aegis-ink transition hover:bg-aegis-panel disabled:opacity-60";

function ToolbarGroup({
  label,
  testId,
  children,
}: {
  label: string;
  testId: string;
  children: ReactNode;
}) {
  return (
    <div className="flex flex-wrap items-center gap-2" data-testid={testId}>
      <span className="text-[0.65rem] font-semibold uppercase tracking-[0.12em] text-aegis-muted">
        {label}
      </span>
      {children}
    </div>
  );
}

export type ResearchAssessmentActionToolbarProps = {
  isPending: boolean;
  activeOutcomeLabelAssessmentId: number | null;
  outcomeLabelHistoryLoadKind: OutcomeLabelHistoryLoadKind | null;
  outcomeLabelHistoryAssessmentId: number | null;
  latestId: number | null;
  readinessStatus: string | null | undefined;
  onRefreshLatest: () => void;
  onRefreshReadiness: () => void;
  onDownloadReadiness: () => void;
  onRefreshEvidenceSummary: () => void;
  onDownloadEvidenceSummary: () => void;
  onDownloadAssessments: () => void;
  onBackfillAssessments: () => void;
  onComputeOutcomeLabels: () => void;
  onBackfillOutcomeLabels: () => void;
  onDownloadOutcomeLabels: () => void;
  onComputeCalibration: () => void;
  onDownloadCalibrations: () => void;
  onAssess: () => void;
};

export function ResearchAssessmentActionToolbar({
  isPending,
  activeOutcomeLabelAssessmentId,
  outcomeLabelHistoryLoadKind,
  outcomeLabelHistoryAssessmentId,
  latestId,
  readinessStatus,
  onRefreshLatest,
  onRefreshReadiness,
  onDownloadReadiness,
  onRefreshEvidenceSummary,
  onDownloadEvidenceSummary,
  onDownloadAssessments,
  onBackfillAssessments,
  onComputeOutcomeLabels,
  onBackfillOutcomeLabels,
  onDownloadOutcomeLabels,
  onComputeCalibration,
  onDownloadCalibrations,
  onAssess,
}: ResearchAssessmentActionToolbarProps) {
  return (
    <>
      <div
        className="flex flex-wrap items-center gap-x-4 gap-y-2"
        data-testid="research-assessment-action-toolbar"
      >
        <ToolbarGroup label="Diagnostics" testId="toolbar-group-diagnostics">
          <button
            type="button"
            onClick={onRefreshLatest}
            disabled={isPending}
            className={BUTTON_CLASS}
          >
            Refresh latest
          </button>
          <button
            type="button"
            onClick={onRefreshReadiness}
            disabled={isPending}
            className={BUTTON_CLASS}
          >
            Refresh readiness
          </button>
          <button
            type="button"
            onClick={onDownloadReadiness}
            disabled={isPending}
            className={BUTTON_CLASS}
          >
            Download readiness JSON
          </button>
          <button
            type="button"
            onClick={onRefreshEvidenceSummary}
            disabled={isPending}
            className={BUTTON_CLASS}
          >
            Refresh evidence summary
          </button>
          <button
            type="button"
            onClick={onDownloadEvidenceSummary}
            disabled={isPending}
            className={BUTTON_CLASS}
          >
            Download evidence JSON
          </button>
        </ToolbarGroup>
        <ToolbarGroup label="Assessments" testId="toolbar-group-assessments">
          <button
            type="button"
            onClick={onDownloadAssessments}
            disabled={isPending}
            className={BUTTON_CLASS}
          >
            Download assessments JSON
          </button>
          <button
            type="button"
            onClick={onBackfillAssessments}
            disabled={isPending}
            className={BUTTON_CLASS}
          >
            Backfill assessments
          </button>
        </ToolbarGroup>
        <ToolbarGroup label="Outcome labels" testId="toolbar-group-outcome-labels">
          <button
            type="button"
            onClick={onComputeOutcomeLabels}
            disabled={isPending || activeOutcomeLabelAssessmentId == null}
            data-testid="compute-outcome-labels"
            aria-label={formatOutcomeLabelActionAriaLabel(
              "Compute outcome labels",
              activeOutcomeLabelAssessmentId,
              outcomeLabelHistoryLoadKind,
            )}
            className={BUTTON_CLASS}
          >
            Compute outcome labels
            {activeOutcomeLabelAssessmentId != null ? (
              <span
                className="ml-1 font-mono text-xs text-aegis-muted"
                data-testid="compute-outcome-labels-id-chip"
              >
                {formatOutcomeLabelActionIdChip(
                  activeOutcomeLabelAssessmentId,
                  outcomeLabelHistoryLoadKind,
                )}
              </span>
            ) : null}
          </button>
          <button
            type="button"
            onClick={onBackfillOutcomeLabels}
            disabled={isPending}
            data-testid="backfill-outcome-labels"
            aria-label={formatOutcomeLabelBackfillAriaLabel(
              activeOutcomeLabelAssessmentId,
              outcomeLabelHistoryLoadKind,
            )}
            className={BUTTON_CLASS}
          >
            Backfill outcome labels
            {activeOutcomeLabelAssessmentId != null ? (
              <span
                className="ml-1 font-mono text-xs text-aegis-muted"
                data-testid="backfill-outcome-labels-id-chip"
              >
                {formatOutcomeLabelActionIdChip(
                  activeOutcomeLabelAssessmentId,
                  outcomeLabelHistoryLoadKind,
                )}
              </span>
            ) : null}
          </button>
          <button
            type="button"
            onClick={onDownloadOutcomeLabels}
            disabled={isPending || activeOutcomeLabelAssessmentId == null}
            data-testid="download-outcome-labels"
            aria-label={formatOutcomeLabelActionAriaLabel(
              "Download outcome labels JSON",
              activeOutcomeLabelAssessmentId,
              outcomeLabelHistoryLoadKind,
            )}
            className={BUTTON_CLASS}
          >
            Download outcome labels JSON
            {activeOutcomeLabelAssessmentId != null ? (
              <span
                className="ml-1 font-mono text-xs text-aegis-muted"
                data-testid="download-outcome-labels-id-chip"
              >
                {formatOutcomeLabelActionIdChip(
                  activeOutcomeLabelAssessmentId,
                  outcomeLabelHistoryLoadKind,
                )}
              </span>
            ) : null}
          </button>
        </ToolbarGroup>
        <ToolbarGroup label="Calibration" testId="toolbar-group-calibration">
          <button
            type="button"
            onClick={onComputeCalibration}
            disabled={isPending || latestId == null || readinessStatus !== "ready"}
            data-testid="compute-calibration"
            aria-label={formatCalibrationActionAriaLabel("Compute calibration", latestId)}
            className={BUTTON_CLASS}
          >
            Compute calibration
            {latestId != null ? (
              <span
                className="ml-1 font-mono text-xs text-aegis-muted"
                data-testid="compute-calibration-id-chip"
              >
                {formatCalibrationActionIdChip(latestId)}
              </span>
            ) : null}
          </button>
          <button
            type="button"
            onClick={onDownloadCalibrations}
            disabled={isPending || latestId == null}
            data-testid="download-calibrations"
            aria-label={formatCalibrationActionAriaLabel("Download calibrations JSON", latestId)}
            className={BUTTON_CLASS}
          >
            Download calibrations JSON
            {latestId != null ? (
              <span
                className="ml-1 font-mono text-xs text-aegis-muted"
                data-testid="download-calibrations-id-chip"
              >
                {formatCalibrationActionIdChip(latestId)}
              </span>
            ) : null}
          </button>
        </ToolbarGroup>
        <button
          type="button"
          onClick={onAssess}
          disabled={isPending}
          className="rounded bg-aegis-ink px-4 py-2 text-sm font-medium text-white transition hover:brightness-110 disabled:opacity-60"
        >
          {isPending ? "Working..." : "Run assessment"}
        </button>
      </div>
      {outcomeLabelHistoryAssessmentId != null &&
      latestId != null &&
      outcomeLabelHistoryAssessmentId !== latestId ? (
        <p
          className="basis-full text-xs text-aegis-muted"
          data-testid="calibration-controls-latest-note"
        >
          Calibration actions use latest assessment {latestId} (panel labels are for{" "}
          {outcomeLabelHistoryAssessmentId}).
        </p>
      ) : null}
    </>
  );
}
