"use client";

import type {
  AssessmentBackfillResponse,
  OutcomeLabelBackfillResponse,
} from "@/lib/api-client";

export type ResearchBackfillStatusSectionProps = {
  backfillSummary: OutcomeLabelBackfillResponse | null;
  assessmentBackfillSummary: AssessmentBackfillResponse | null;
};

export function ResearchBackfillStatusSection({
  backfillSummary,
  assessmentBackfillSummary,
}: ResearchBackfillStatusSectionProps) {
  if (backfillSummary == null && assessmentBackfillSummary == null) {
    return null;
  }

  return (
    <div data-testid="backfill-status-section">
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
    </div>
  );
}
