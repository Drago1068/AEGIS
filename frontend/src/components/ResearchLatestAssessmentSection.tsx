"use client";

import type { ResearchAssessment } from "@/lib/api-client";

export type ResearchLatestAssessmentSectionProps = {
  latest: ResearchAssessment;
};

export function ResearchLatestAssessmentSection({
  latest,
}: ResearchLatestAssessmentSectionProps) {
  return (
    <div data-testid="latest-assessment-section">
      <p className="font-semibold uppercase tracking-wide text-aegis-warn">
        State: {latest.state.replaceAll("_", " ")}
      </p>
      <dl className="mt-3 grid gap-2 sm:grid-cols-2">
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
            {latest.lookback_start_date} → {latest.lookback_end_date} ({latest.bar_count}{" "}
            bars)
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
      <p className="mt-3 text-xs text-aegis-muted">
        Computed at {latest.computed_at} from source {latest.input_source}. Research only —
        not actionable.
      </p>
    </div>
  );
}
