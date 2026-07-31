/**
 * Pure presentation helpers for ResearchAssessmentPanel outcome-label UX.
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
