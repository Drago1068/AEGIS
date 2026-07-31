"use client";

import type { ProbabilityCalibration } from "@/lib/api-client";

export type ResearchProbabilityCalibrationSectionProps = {
  calibration: ProbabilityCalibration;
  calibrationHistory: ProbabilityCalibration[];
};

export function ResearchProbabilityCalibrationSection({
  calibration,
  calibrationHistory,
}: ResearchProbabilityCalibrationSectionProps) {
  return (
    <div
      className="rounded border border-aegis-line bg-white/60 p-3"
      data-testid="probability-calibration-section"
    >
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
  );
}
