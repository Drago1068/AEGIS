"use client";

import type { ReactNode } from "react";

export type ResearchAssessmentPanelHeaderProps = {
  children: ReactNode;
};

export function ResearchAssessmentPanelHeader({
  children,
}: ResearchAssessmentPanelHeaderProps) {
  return (
    <header
      className="mb-4 flex flex-wrap items-start justify-between gap-3"
      data-testid="research-assessment-panel-header"
    >
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
      {children}
    </header>
  );
}
