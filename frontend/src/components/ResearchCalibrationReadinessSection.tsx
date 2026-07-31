"use client";

import type { CalibrationReadiness } from "@/lib/api-client";

export type ResearchCalibrationReadinessSectionProps = {
  readiness: CalibrationReadiness;
};

export function ResearchCalibrationReadinessSection({
  readiness,
}: ResearchCalibrationReadinessSectionProps) {
  return (
    <div
      className="rounded border border-aegis-line bg-white/60 p-3"
      data-testid="calibration-readiness-section"
    >
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
  );
}
