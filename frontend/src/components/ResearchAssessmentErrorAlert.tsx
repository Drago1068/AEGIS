"use client";

export type ResearchAssessmentErrorAlertProps = {
  error: string | null;
};

export function ResearchAssessmentErrorAlert({
  error,
}: ResearchAssessmentErrorAlertProps) {
  if (error == null) {
    return null;
  }

  return (
    <p
      className="mb-3 text-sm text-aegis-danger"
      role="alert"
      data-testid="research-assessment-error"
    >
      {error}
    </p>
  );
}
