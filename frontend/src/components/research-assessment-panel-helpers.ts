/**
 * Pure presentation helpers for ResearchAssessmentPanel outcome-label / calibration UX.
 * No market math, recommendations, or trading logic.
 */

export type OutcomeLabelHistoryLoadKind = "latest" | "scan_labeled";

/** Matches backend FORWARD_HORIZON_SESSIONS (ADR-0314 / ADR-0320). Display-only; never invents values. */
export const CONFIGURED_FORWARD_HORIZON_SESSIONS = [5, 20] as const;

/** True when ``labels`` includes every configured ``forward_return_N`` key (ADR-0320). */
export function labelCoversConfiguredHorizons(
  labels: Record<string, number>,
  horizons: readonly number[] = CONFIGURED_FORWARD_HORIZON_SESSIONS,
): boolean {
  return horizons.every((horizon) =>
    Object.prototype.hasOwnProperty.call(labels, `forward_return_${horizon}`),
  );
}

/** Research-only complete/partial coverage label from existing keys only. */
export function formatLabelHorizonCoverage(
  labels: Record<string, number>,
  horizons: readonly number[] = CONFIGURED_FORWARD_HORIZON_SESSIONS,
): { coverage: "complete" | "partial"; presentKeys: string; missingKeys: string } {
  const required = horizons.map((horizon) => `forward_return_${horizon}`);
  const present = required.filter((key) =>
    Object.prototype.hasOwnProperty.call(labels, key),
  );
  const missing = required.filter((key) => !Object.prototype.hasOwnProperty.call(labels, key));
  return {
    coverage: missing.length === 0 ? "complete" : "partial",
    presentKeys: present.length > 0 ? present.join(",") : "none",
    missingKeys: missing.length > 0 ? missing.join(",") : "none",
  };
}

/** Sort API label keys: forward_return_N by N ascending, then other keys. Never invent values. */
export function sortedLabelEntries(labels: Record<string, number>): [string, number][] {
  return Object.entries(labels).sort(([a], [b]) => {
    const na = /^forward_return_(\d+)$/.exec(a);
    const nb = /^forward_return_(\d+)$/.exec(b);
    if (na && nb) {
      return Number(na[1]) - Number(nb[1]);
    }
    if (na) {
      return -1;
    }
    if (nb) {
      return 1;
    }
    return a.localeCompare(b);
  });
}

/** Compact history line from API label payload only (Phase 26 + Phase 30). */
export function formatLabelHorizonSummary(
  labels: Record<string, number>,
  endDates?: Record<string, string>,
): string {
  const entries = sortedLabelEntries(labels);
  if (entries.length === 0) {
    return "none";
  }
  return entries
    .map(([key, value]) => {
      const match = /^forward_return_(\d+)$/.exec(key);
      const short = match ? `fwd${match[1]}` : key;
      const end = endDates?.[key];
      const endPart = typeof end === "string" && end.length > 0 ? ` end=${end}` : "";
      return `${short}=${value.toFixed(4)}${endPart}`;
    })
    .join(" · ");
}

/** Prefer tracked load-kind; otherwise infer from whether assessment matches latest. */
export function resolveOutcomeLabelHistoryLoadKind(
  assessmentId: number,
  loadKind: OutcomeLabelHistoryLoadKind | null,
  latestId: number | null | undefined,
): OutcomeLabelHistoryLoadKind {
  return loadKind ?? (latestId != null && assessmentId === latestId ? "latest" : "scan_labeled");
}

/** Accessible name for compute/download outcome-label actions (Phase 113 / 309). */
export function formatOutcomeLabelActionAriaLabel(
  action:
    | "Compute outcome labels"
    | "Compute ready-horizon labels"
    | "Download outcome labels JSON",
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

/** Accessible name for ready-horizons backfill (Phase 311). */
export function formatReadyHorizonsBackfillAriaLabel(
  assessmentId: number | null,
  loadKind: OutcomeLabelHistoryLoadKind | null,
): string {
  if (assessmentId == null) {
    return "Backfill ready-horizon labels";
  }
  const kindSuffix =
    loadKind === "scan_labeled"
      ? " (scan-labeled)"
      : loadKind === "latest"
        ? " (latest)"
        : "";
  return `Backfill ready-horizon labels then refresh assessment ${assessmentId}${kindSuffix}`;
}

/** Compact assessment history line from API payload only (Phase 28/61). */
export function formatAssessmentHistoryRow(row: {
  computed_at: string;
  coverage_confidence: number;
  probability_confidence: number | null;
  input_source: string;
  components: {
    research_index?: number | null;
    component_source?: string | null;
  };
}): string {
  const index = row.components.research_index;
  const indexLabel =
    typeof index === "number" ? `index=${index.toFixed(4)}` : "index=n/a";
  const cov = `cov=${row.coverage_confidence.toFixed(4)}`;
  const p =
    row.probability_confidence === null
      ? "p=null"
      : `p=${row.probability_confidence.toFixed(4)}`;
  const srcRaw = row.components.component_source;
  const src =
    typeof srcRaw === "string" && srcRaw.trim()
      ? srcRaw
      : row.input_source;
  return `${row.computed_at} · ${indexLabel} · ${cov} · ${p} · src=${src}`;
}

const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;

/**
 * Keep the newest assessment per as_of_trading_date (newest-first input).
 * Matches chart as_of dedupe. Skips invalid dates; never invents rows (ADR-0306).
 */
export function distinctAsOfAssessments<
  T extends { as_of_trading_date: string },
>(assessments: T[]): T[] {
  const seen = new Set<string>();
  const out: T[] = [];
  for (const row of assessments) {
    const date = row.as_of_trading_date;
    if (typeof date !== "string" || !ISO_DATE.test(date)) {
      continue;
    }
    if (seen.has(date)) {
      continue;
    }
    seen.add(date);
    out.push(row);
  }
  return out;
}

export const ASSESSMENT_SOURCE_FILTER_OPTIONS = [
  { value: "", label: "All sources" },
  { value: "mixed", label: "mixed (cross-source fill)" },
  { value: "alpha_vantage", label: "alpha_vantage" },
  { value: "polygon", label: "polygon" },
] as const;
