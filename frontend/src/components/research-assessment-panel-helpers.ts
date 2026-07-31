/**
 * Pure presentation helpers for ResearchAssessmentPanel outcome-label / calibration UX.
 * No market math, recommendations, or trading logic.
 */

export type OutcomeLabelHistoryLoadKind = "latest" | "scan_labeled";

/** Prefer tracked load-kind; otherwise infer from whether assessment matches latest. */
export function resolveOutcomeLabelHistoryLoadKind(
  assessmentId: number,
  loadKind: OutcomeLabelHistoryLoadKind | null,
  latestId: number | null | undefined,
): OutcomeLabelHistoryLoadKind {
  return loadKind ?? (latestId != null && assessmentId === latestId ? "latest" : "scan_labeled");
}

/** Accessible name for compute/download outcome-label actions (Phase 113). */
export function formatOutcomeLabelActionAriaLabel(
  action: "Compute outcome labels" | "Download outcome labels JSON",
  assessmentId: number | null,
  loadKind: OutcomeLabelHistoryLoadKind | null,
): string {
  if (assessmentId == null) {
    return action;
  }
  const kindSuffix =
    loadKind === "scan_labeled"
      ? " (scan-labeled)"
      : loadKind === "latest"
        ? " (latest)"
        : "";
  return `${action} for assessment ${assessmentId}${kindSuffix}`;
}

/** Visible id chip for compute/download outcome-label actions (Phase 117). */
export function formatOutcomeLabelActionIdChip(
  assessmentId: number,
  loadKind: OutcomeLabelHistoryLoadKind | null,
): string {
  if (loadKind === "scan_labeled") {
    return `(${assessmentId} · scan-labeled)`;
  }
  if (loadKind === "latest") {
    return `(${assessmentId} · latest)`;
  }
  return `(${assessmentId})`;
}

/** Accessible name for compute/download calibration actions (Phase 119; always latest). */
export function formatCalibrationActionAriaLabel(
  action: "Compute calibration" | "Download calibrations JSON",
  assessmentId: number | null,
): string {
  if (assessmentId == null) {
    return action;
  }
  return `${action} for assessment ${assessmentId} (latest)`;
}

/** Visible id chip for compute/download calibration actions (Phase 119; always latest). */
export function formatCalibrationActionIdChip(assessmentId: number): string {
  return `(${assessmentId} · latest)`;
}

/** Accessible name for outcome-label backfill when a refresh target is known (Phase 121). */
export function formatOutcomeLabelBackfillAriaLabel(
  assessmentId: number | null,
  loadKind: OutcomeLabelHistoryLoadKind | null,
): string {
  if (assessmentId == null) {
    return "Backfill outcome labels";
  }
  const kindSuffix =
    loadKind === "scan_labeled"
      ? " (scan-labeled)"
      : loadKind === "latest"
        ? " (latest)"
        : "";
  return `Backfill outcome labels then refresh assessment ${assessmentId}${kindSuffix}`;
}
