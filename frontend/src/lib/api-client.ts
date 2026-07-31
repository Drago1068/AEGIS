/**
 * Typed HTTP client for the AEGIS backend API.
 *
 * Types here must stay in sync with the backend's Pydantic response schemas under
 * `backend/src/aegis/api/schemas/`. See ADR-0004 for the Phase 3 operator console contract,
 * ADR-0005 for Phase 4 operator authentication, and ADR-0007 for Phase 6 research
 * assessments.
 */

export interface HealthResponse {
  status: "ok";
}

export interface DependencyStatus {
  database: "ok" | "unavailable";
  redis: "ok" | "unavailable";
}

export interface ReadyResponse {
  status: "ready";
  checks: DependencyStatus;
}

export interface NotReadyResponse {
  status: "unavailable";
  checks: DependencyStatus;
}

export interface WatchlistSymbol {
  symbol: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface DailyBar {
  source: string;
  symbol: string;
  trading_date: string;
  open: string;
  high: string;
  low: string;
  close: string;
  volume: number;
  data_quality: string;
  schema_version: number;
  ingested_at: string;
}

export interface IngestionSymbolResult {
  symbol: string;
  stored_count: number;
  skipped_existing_count: number;
  rejected_count: number;
  rejections: Record<string, number>;
  error: string | null;
}

export interface IngestionRunResponse {
  results: IngestionSymbolResult[];
}

export interface ResearchAssessment {
  id?: number | null;
  symbol: string;
  method_id: string;
  method_version: number;
  state: string;
  as_of_trading_date: string;
  event_time: string;
  computed_at: string;
  coverage_confidence: number;
  /** Always null when not calibrated. Never merge with coverage_confidence. */
  probability_confidence: number | null;
  /** Research metrics plus optional Phase 11 provenance / factor fields (schema_version 2). */
  components: {
    total_return_20: number;
    realized_vol_20: number;
    research_index: number;
    [key: string]: unknown;
  };
  schema_version: number;
  input_source: string;
  lookback_start_date: string;
  lookback_end_date: string;
  bar_count: number;
}

export interface OperatorMe {
  username: string;
}

/** Options for authenticated API calls (cookie forwarding for SSR, 401 redirect control). */
export type ApiRequestOptions = {
  /** Skip browser redirect to /login on HTTP 401 (login form and auth probes). */
  skipAuthRedirect?: boolean;
  /** Forward Cookie header for server-side fetches (browser cookies are not automatic). */
  cookie?: string;
};

export class ApiClientError extends Error {
  readonly status: number;
  readonly body: unknown;

  constructor(message: string, status: number, body: unknown = null) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.body = body;
  }
}

async function readJson(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

function redirectToLoginIfNeeded(status: number, options?: ApiRequestOptions): void {
  if (status !== 401 || options?.skipAuthRedirect) {
    return;
  }
  if (typeof window === "undefined") {
    return;
  }
  if (window.location.pathname.startsWith("/login")) {
    return;
  }
  window.location.assign("/login");
}

async function requestJson(
  url: string,
  init?: RequestInit,
  options?: ApiRequestOptions,
): Promise<{ response: Response; body: unknown }> {
  const headers = new Headers(init?.headers);
  if (options?.cookie) {
    headers.set("Cookie", options.cookie);
  }
  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }

  const response = await fetch(url, {
    ...init,
    headers,
    credentials: "include",
  });
  const body = await readJson(response);
  redirectToLoginIfNeeded(response.status, options);
  return { response, body };
}

export async function getHealth(baseUrl: string): Promise<HealthResponse> {
  const { response, body } = await requestJson(`${baseUrl}/health`, undefined, {
    skipAuthRedirect: true,
  });
  if (!response.ok) {
    throw new ApiClientError(`Unexpected /health status: ${response.status}`, response.status, body);
  }
  return body as HealthResponse;
}

export async function getReady(
  baseUrl: string,
): Promise<{ ok: true; body: ReadyResponse } | { ok: false; body: NotReadyResponse }> {
  const { response, body } = await requestJson(`${baseUrl}/ready`, undefined, {
    skipAuthRedirect: true,
  });
  if (response.status === 200) {
    return { ok: true, body: body as ReadyResponse };
  }
  return { ok: false, body: body as NotReadyResponse };
}

export async function login(
  baseUrl: string,
  username: string,
  password: string,
): Promise<OperatorMe> {
  const { response, body } = await requestJson(
    `${baseUrl}/auth/login`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ username, password }),
    },
    { skipAuthRedirect: true },
  );
  if (!response.ok) {
    throw new ApiClientError(
      `Unexpected POST /auth/login status: ${response.status}`,
      response.status,
      body,
    );
  }
  return body as OperatorMe;
}

export async function logout(baseUrl: string, options?: ApiRequestOptions): Promise<void> {
  const { response, body } = await requestJson(
    `${baseUrl}/auth/logout`,
    { method: "POST" },
    options,
  );
  if (!response.ok) {
    throw new ApiClientError(
      `Unexpected POST /auth/logout status: ${response.status}`,
      response.status,
      body,
    );
  }
}

export async function getMe(baseUrl: string, options?: ApiRequestOptions): Promise<OperatorMe> {
  const { response, body } = await requestJson(`${baseUrl}/auth/me`, undefined, options);
  if (!response.ok) {
    throw new ApiClientError(
      `Unexpected GET /auth/me status: ${response.status}`,
      response.status,
      body,
    );
  }
  return body as OperatorMe;
}

export async function listWatchlist(
  baseUrl: string,
  options?: ApiRequestOptions,
): Promise<WatchlistSymbol[]> {
  const { response, body } = await requestJson(`${baseUrl}/watchlist`, undefined, options);
  if (!response.ok) {
    throw new ApiClientError(
      `Unexpected /watchlist status: ${response.status}`,
      response.status,
      body,
    );
  }
  return body as WatchlistSymbol[];
}

export async function addWatchlistSymbol(
  baseUrl: string,
  symbol: string,
  options?: ApiRequestOptions,
): Promise<WatchlistSymbol> {
  const { response, body } = await requestJson(
    `${baseUrl}/watchlist`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ symbol }),
    },
    options,
  );
  if (!response.ok) {
    throw new ApiClientError(
      `Unexpected POST /watchlist status: ${response.status}`,
      response.status,
      body,
    );
  }
  return body as WatchlistSymbol;
}

export async function removeWatchlistSymbol(
  baseUrl: string,
  symbol: string,
  options?: ApiRequestOptions,
): Promise<void> {
  const { response, body } = await requestJson(
    `${baseUrl}/watchlist/${encodeURIComponent(symbol)}`,
    { method: "DELETE" },
    options,
  );
  if (!response.ok) {
    throw new ApiClientError(
      `Unexpected DELETE /watchlist/{symbol} status: ${response.status}`,
      response.status,
      body,
    );
  }
}

export async function listDailyBars(
  baseUrl: string,
  symbol: string,
  limit = 100,
  options?: ApiRequestOptions,
): Promise<DailyBar[]> {
  const url = `${baseUrl}/market-data/${encodeURIComponent(symbol)}/daily-bars?limit=${limit}`;
  const { response, body } = await requestJson(url, undefined, options);
  if (response.status === 404) {
    throw new ApiClientError(`No stored daily bars for ${symbol}`, 404, body);
  }
  if (!response.ok) {
    throw new ApiClientError(
      `Unexpected daily-bars status: ${response.status}`,
      response.status,
      body,
    );
  }
  return body as DailyBar[];
}

export async function ingestMarketData(
  baseUrl: string,
  options?: ApiRequestOptions,
): Promise<IngestionRunResponse> {
  const { response, body } = await requestJson(
    `${baseUrl}/market-data/ingest`,
    {
      method: "POST",
      headers: { Accept: "application/json" },
    },
    options,
  );
  if (!response.ok) {
    throw new ApiClientError(
      `Unexpected POST /market-data/ingest status: ${response.status}`,
      response.status,
      body,
    );
  }
  return body as IngestionRunResponse;
}

export async function createResearchAssessment(
  baseUrl: string,
  symbol: string,
  options?: ApiRequestOptions,
): Promise<ResearchAssessment> {
  const { response, body } = await requestJson(
    `${baseUrl}/research/${encodeURIComponent(symbol)}/assessments`,
    {
      method: "POST",
      headers: { Accept: "application/json" },
    },
    options,
  );
  if (!response.ok) {
    throw new ApiClientError(
      `Unexpected POST /research/{symbol}/assessments status: ${response.status}`,
      response.status,
      body,
    );
  }
  return body as ResearchAssessment;
}

export interface AssessmentBackfillItem {
  symbol: string;
  as_of_trading_date: string;
  persisted: boolean;
  assessment_snapshot_id?: number | null;
  reason?: string | null;
  detail?: string | null;
}

export interface AssessmentBackfillResponse {
  symbol: string;
  candidate_count: number;
  persisted_count: number;
  skipped_count: number;
  outcomes: AssessmentBackfillItem[];
  detail: string;
}

/** Create point-in-time assessments for recent primary bar dates (Phase 45, ADR-0046). */
export async function backfillResearchAssessments(
  baseUrl: string,
  symbol: string,
  limit = 20,
  options?: ApiRequestOptions,
): Promise<AssessmentBackfillResponse> {
  const url =
    `${baseUrl}/research/${encodeURIComponent(symbol)}/assessments/backfill` +
    `?limit=${encodeURIComponent(String(limit))}`;
  const { response, body } = await requestJson(
    url,
    {
      method: "POST",
      headers: { Accept: "application/json" },
    },
    options,
  );
  if (!response.ok) {
    throw new ApiClientError(
      `Unexpected POST assessments/backfill status: ${response.status}`,
      response.status,
      body,
    );
  }
  return body as AssessmentBackfillResponse;
}

export async function listResearchAssessments(
  baseUrl: string,
  symbol: string,
  limit = 20,
  options?: ApiRequestOptions & { componentSource?: string | null },
): Promise<ResearchAssessment[]> {
  const params = new URLSearchParams({ limit: String(limit) });
  const source = options?.componentSource?.trim();
  if (source) {
    params.set("component_source", source);
  }
  const url =
    `${baseUrl}/research/${encodeURIComponent(symbol)}/assessments` +
    `?${params.toString()}`;
  const { response, body } = await requestJson(url, undefined, options);
  if (!response.ok) {
    throw new ApiClientError(
      `Unexpected GET /research/{symbol}/assessments status: ${response.status}`,
      response.status,
      body,
    );
  }
  return body as ResearchAssessment[];
}

/** Download assessment history JSON attachment (Phase 38/61, ADR-0039 / ADR-0062). */
export async function downloadResearchAssessments(
  baseUrl: string,
  symbol: string,
  limit = 20,
  options?: ApiRequestOptions & { componentSource?: string | null },
): Promise<string> {
  const params = new URLSearchParams({ limit: String(limit) });
  const source = options?.componentSource?.trim();
  if (source) {
    params.set("component_source", source);
  }
  const url =
    `${baseUrl}/research/${encodeURIComponent(symbol)}/assessments/export` +
    `?${params.toString()}`;
  const headers = new Headers();
  if (options?.cookie) {
    headers.set("Cookie", options.cookie);
  }
  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }

  const response = await fetch(url, {
    headers,
    credentials: "include",
  });
  redirectToLoginIfNeeded(response.status, options);
  if (!response.ok) {
    const body = await readJson(response);
    throw new ApiClientError(
      `Unexpected GET assessments export status: ${response.status}`,
      response.status,
      body,
    );
  }

  const blob = await response.blob();
  const filename =
    parseContentDispositionFilename(response.headers.get("Content-Disposition")) ??
    `aegis-${symbol.toUpperCase()}-assessments.json`;

  if (typeof window !== "undefined") {
    const objectUrl = URL.createObjectURL(blob);
    try {
      const anchor = document.createElement("a");
      anchor.href = objectUrl;
      anchor.download = filename;
      anchor.rel = "noopener";
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
    } finally {
      URL.revokeObjectURL(objectUrl);
    }
  }

  return filename;
}

export async function getLatestResearchAssessment(
  baseUrl: string,
  symbol: string,
  options?: ApiRequestOptions,
): Promise<ResearchAssessment> {
  const url = `${baseUrl}/research/${encodeURIComponent(symbol)}/assessments/latest`;
  const { response, body } = await requestJson(url, undefined, options);
  if (response.status === 404) {
    throw new ApiClientError(`No research assessment for ${symbol}`, 404, body);
  }
  if (!response.ok) {
    throw new ApiClientError(
      `Unexpected GET /research/{symbol}/assessments/latest status: ${response.status}`,
      response.status,
      body,
    );
  }
  return body as ResearchAssessment;
}

export interface OutcomeLabel {
  id?: number | null;
  assessment_snapshot_id: number;
  symbol: string;
  label_method_id: string;
  label_method_version: number;
  state: string;
  as_of_trading_date: string;
  computed_at: string;
  labels: Record<string, number>;
  label_end_dates: Record<string, string>;
  schema_version: number;
  bar_source: string;
}

export async function createOutcomeLabels(
  baseUrl: string,
  symbol: string,
  assessmentId: number,
  options?: ApiRequestOptions,
): Promise<OutcomeLabel> {
  const url =
    `${baseUrl}/research/${encodeURIComponent(symbol)}/assessments/` +
    `${assessmentId}/outcome-labels`;
  const { response, body } = await requestJson(
    url,
    {
      method: "POST",
      headers: { Accept: "application/json" },
    },
    options,
  );
  if (!response.ok) {
    throw new ApiClientError(
      `Unexpected POST outcome-labels status: ${response.status}`,
      response.status,
      body,
    );
  }
  return body as OutcomeLabel;
}

export interface OutcomeLabelBackfillItem {
  symbol: string;
  assessment_snapshot_id: number;
  persisted: boolean;
  reason?: string | null;
  detail?: string | null;
}

export interface OutcomeLabelBackfillResponse {
  symbol: string;
  assessment_count: number;
  persisted_count: number;
  skipped_count: number;
  outcomes: OutcomeLabelBackfillItem[];
  detail: string;
}

/** Re-attempt Phase 13 labeling over recent assessment history (Phase 43/57). */
export async function backfillOutcomeLabels(
  baseUrl: string,
  symbol: string,
  limit = 100,
  options?: ApiRequestOptions,
): Promise<OutcomeLabelBackfillResponse> {
  const url =
    `${baseUrl}/research/${encodeURIComponent(symbol)}/outcome-labels/backfill` +
    `?limit=${encodeURIComponent(String(limit))}`;
  const { response, body } = await requestJson(
    url,
    {
      method: "POST",
      headers: { Accept: "application/json" },
    },
    options,
  );
  if (!response.ok) {
    throw new ApiClientError(
      `Unexpected POST outcome-labels/backfill status: ${response.status}`,
      response.status,
      body,
    );
  }
  return body as OutcomeLabelBackfillResponse;
}

export async function getLatestOutcomeLabels(
  baseUrl: string,
  symbol: string,
  assessmentId: number,
  options?: ApiRequestOptions,
): Promise<OutcomeLabel> {
  const url =
    `${baseUrl}/research/${encodeURIComponent(symbol)}/assessments/` +
    `${assessmentId}/outcome-labels/latest`;
  const { response, body } = await requestJson(url, undefined, options);
  if (response.status === 404) {
    throw new ApiClientError(`No outcome labels for assessment ${assessmentId}`, 404, body);
  }
  if (!response.ok) {
    throw new ApiClientError(
      `Unexpected GET outcome-labels/latest status: ${response.status}`,
      response.status,
      body,
    );
  }
  return body as OutcomeLabel;
}

export async function listOutcomeLabels(
  baseUrl: string,
  symbol: string,
  assessmentId: number,
  limit = 20,
  options?: ApiRequestOptions,
): Promise<OutcomeLabel[]> {
  const url =
    `${baseUrl}/research/${encodeURIComponent(symbol)}/assessments/` +
    `${assessmentId}/outcome-labels?limit=${encodeURIComponent(String(limit))}`;
  const { response, body } = await requestJson(url, undefined, options);
  if (!response.ok) {
    throw new ApiClientError(
      `Unexpected GET outcome-labels status: ${response.status}`,
      response.status,
      body,
    );
  }
  if (!Array.isArray(body)) {
    throw new ApiClientError("Unexpected outcome-labels list payload", response.status, body);
  }
  return body as OutcomeLabel[];
}

/** Download outcome-label history JSON attachment (Phase 34, ADR-0035). */
export async function downloadOutcomeLabels(
  baseUrl: string,
  symbol: string,
  assessmentId: number,
  limit = 20,
  options?: ApiRequestOptions,
): Promise<string> {
  const url =
    `${baseUrl}/research/${encodeURIComponent(symbol)}/assessments/` +
    `${assessmentId}/outcome-labels/export?limit=${encodeURIComponent(String(limit))}`;
  const headers = new Headers();
  if (options?.cookie) {
    headers.set("Cookie", options.cookie);
  }
  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }

  const response = await fetch(url, {
    headers,
    credentials: "include",
  });
  redirectToLoginIfNeeded(response.status, options);
  if (!response.ok) {
    const body = await readJson(response);
    throw new ApiClientError(
      `Unexpected GET outcome-labels export status: ${response.status}`,
      response.status,
      body,
    );
  }

  const blob = await response.blob();
  const filename =
    parseContentDispositionFilename(response.headers.get("Content-Disposition")) ??
    `aegis-${symbol.toUpperCase()}-assessment-${assessmentId}-outcome-labels.json`;

  if (typeof window !== "undefined") {
    const objectUrl = URL.createObjectURL(blob);
    try {
      const anchor = document.createElement("a");
      anchor.href = objectUrl;
      anchor.download = filename;
      anchor.rel = "noopener";
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
    } finally {
      URL.revokeObjectURL(objectUrl);
    }
  }

  return filename;
}

/** Download calibration history JSON attachment (Phase 36, ADR-0037). */
export async function downloadProbabilityCalibrations(
  baseUrl: string,
  symbol: string,
  assessmentId: number,
  limit = 20,
  options?: ApiRequestOptions,
): Promise<string> {
  const url =
    `${baseUrl}/research/${encodeURIComponent(symbol)}/assessments/` +
    `${assessmentId}/calibrations/export?limit=${encodeURIComponent(String(limit))}`;
  const headers = new Headers();
  if (options?.cookie) {
    headers.set("Cookie", options.cookie);
  }
  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }

  const response = await fetch(url, {
    headers,
    credentials: "include",
  });
  redirectToLoginIfNeeded(response.status, options);
  if (!response.ok) {
    const body = await readJson(response);
    throw new ApiClientError(
      `Unexpected GET calibrations export status: ${response.status}`,
      response.status,
      body,
    );
  }

  const blob = await response.blob();
  const filename =
    parseContentDispositionFilename(response.headers.get("Content-Disposition")) ??
    `aegis-${symbol.toUpperCase()}-assessment-${assessmentId}-calibrations.json`;

  if (typeof window !== "undefined") {
    const objectUrl = URL.createObjectURL(blob);
    try {
      const anchor = document.createElement("a");
      anchor.href = objectUrl;
      anchor.download = filename;
      anchor.rel = "noopener";
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
    } finally {
      URL.revokeObjectURL(objectUrl);
    }
  }

  return filename;
}

export interface CalibrationHorizonReadiness {
  outcome_horizon_key: string;
  status: string;
  corpus_count: number;
  bucket_count: number;
  detail: string;
}

export interface CalibrationReadiness {
  symbol: string;
  status: string;
  assessment_snapshot_id: number | null;
  research_index: number | null;
  corpus_count: number;
  bucket_count: number;
  min_corpus: number;
  min_bucket: number;
  index_bucket_width: number;
  calibration_method_id: string;
  detail: string;
  outcome_horizon_key?: string;
  by_horizon?: CalibrationHorizonReadiness[];
}

export async function getCalibrationReadiness(
  baseUrl: string,
  symbol: string,
  options?: ApiRequestOptions,
): Promise<CalibrationReadiness> {
  const url = `${baseUrl}/research/${encodeURIComponent(symbol)}/calibration-readiness`;
  const { response, body } = await requestJson(url, undefined, options);
  if (!response.ok) {
    throw new ApiClientError(
      `Unexpected GET /research/{symbol}/calibration-readiness status: ${response.status}`,
      response.status,
      body,
    );
  }
  return body as CalibrationReadiness;
}

/** Download calibration readiness JSON attachment (Phase 32, ADR-0033). */
export async function downloadCalibrationReadiness(
  baseUrl: string,
  symbol: string,
  options?: ApiRequestOptions,
): Promise<string> {
  const url =
    `${baseUrl}/research/${encodeURIComponent(symbol)}/calibration-readiness/export`;
  const headers = new Headers();
  if (options?.cookie) {
    headers.set("Cookie", options.cookie);
  }
  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }

  const response = await fetch(url, {
    headers,
    credentials: "include",
  });
  redirectToLoginIfNeeded(response.status, options);
  if (!response.ok) {
    const body = await readJson(response);
    throw new ApiClientError(
      `Unexpected GET calibration-readiness export status: ${response.status}`,
      response.status,
      body,
    );
  }

  const blob = await response.blob();
  const filename =
    parseContentDispositionFilename(response.headers.get("Content-Disposition")) ??
    `aegis-${symbol.toUpperCase()}-calibration-readiness.json`;

  if (typeof window !== "undefined") {
    const objectUrl = URL.createObjectURL(blob);
    try {
      const anchor = document.createElement("a");
      anchor.href = objectUrl;
      anchor.download = filename;
      anchor.rel = "noopener";
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
    } finally {
      URL.revokeObjectURL(objectUrl);
    }
  }

  return filename;
}

export interface ProbabilityCalibration {
  id?: number | null;
  assessment_snapshot_id: number;
  symbol: string;
  calibration_method_id: string;
  calibration_method_version: number;
  outcome_horizon_key?: string;
  state: string;
  computed_at: string;
  probability_confidence: number;
  corpus_count: number;
  bucket_count: number;
  schema_version: number;
}

export async function createProbabilityCalibration(
  baseUrl: string,
  symbol: string,
  assessmentId: number,
  horizon = "forward_return_5",
  options?: ApiRequestOptions,
): Promise<ProbabilityCalibration> {
  const url =
    `${baseUrl}/research/${encodeURIComponent(symbol)}/assessments/` +
    `${assessmentId}/calibrations?horizon=${encodeURIComponent(horizon)}`;
  const { response, body } = await requestJson(
    url,
    {
      method: "POST",
      headers: { Accept: "application/json" },
    },
    options,
  );
  if (!response.ok) {
    throw new ApiClientError(
      `Unexpected POST calibrations status: ${response.status}`,
      response.status,
      body,
    );
  }
  return body as ProbabilityCalibration;
}

export async function getLatestProbabilityCalibration(
  baseUrl: string,
  symbol: string,
  assessmentId: number,
  options?: ApiRequestOptions,
): Promise<ProbabilityCalibration> {
  const url =
    `${baseUrl}/research/${encodeURIComponent(symbol)}/assessments/` +
    `${assessmentId}/calibrations/latest`;
  const { response, body } = await requestJson(url, undefined, options);
  if (response.status === 404) {
    throw new ApiClientError(
      `No probability calibration for assessment ${assessmentId}`,
      404,
      body,
    );
  }
  if (!response.ok) {
    throw new ApiClientError(
      `Unexpected GET calibrations/latest status: ${response.status}`,
      response.status,
      body,
    );
  }
  return body as ProbabilityCalibration;
}

export async function listProbabilityCalibrations(
  baseUrl: string,
  symbol: string,
  assessmentId: number,
  limit = 20,
  options?: ApiRequestOptions,
): Promise<ProbabilityCalibration[]> {
  const url =
    `${baseUrl}/research/${encodeURIComponent(symbol)}/assessments/` +
    `${assessmentId}/calibrations?limit=${encodeURIComponent(String(limit))}`;
  const { response, body } = await requestJson(url, undefined, options);
  if (!response.ok) {
    throw new ApiClientError(
      `Unexpected GET calibrations status: ${response.status}`,
      response.status,
      body,
    );
  }
  if (!Array.isArray(body)) {
    throw new ApiClientError("Unexpected calibrations list payload", response.status, body);
  }
  return body as ProbabilityCalibration[];
}

export interface ResearchEvidenceSummary {
  symbol: string;
  state: string;
  latest_assessment: ResearchAssessment | null;
  calibration_readiness: CalibrationReadiness;
  latest_outcome_label: OutcomeLabel | null;
  latest_calibration: ProbabilityCalibration | null;
  assessment_count: number;
  /** Scanned ≤100 assessments with a default-method outcome label. */
  labeled_assessment_count: number;
  /** Scanned ≤100 assessments lacking a default-method outcome label. */
  unlabeled_assessment_count: number;
  outcome_label_count: number;
  calibration_count: number;
  /** Component series source for latest assessment; may be "mixed". Null when no assessment. */
  latest_component_source: string | null;
  /** Label bar source for latest assessment (persisted label preferred). */
  latest_resolved_label_bar_source: string | null;
  /** Count of newest ≤100 assessments with component_source "mixed". */
  mixed_component_source_assessment_count: number;
  /** Mixed assessments among the scanned set that still lack a default-method label. */
  mixed_unlabeled_assessment_count: number;
  /** Mixed assessments among the scanned set that have a default-method label. */
  mixed_labeled_assessment_count: number;
  /** bar_source from the newest labeled mixed assessment; null when none labeled. */
  latest_mixed_label_bar_source: string | null;
  /** Newest labeled assessment id in the ≤100 scan; may differ from latest_assessment. */
  most_recent_labeled_assessment_id: number | null;
  /** Newest labeled outcome in the ≤100 scan; never invented. */
  most_recent_labeled_outcome_label: OutcomeLabel | null;
  /** coverage_confidence from latest assessment; null when none. Distinct from probability. */
  latest_coverage_confidence: number | null;
  /** research_index from latest assessment components when numeric; null otherwise. */
  latest_research_index: number | null;
  /** as_of_trading_date from latest assessment (ISO date); null when none. */
  latest_as_of_trading_date: string | null;
  /** bar_count from latest assessment; null when none. */
  latest_bar_count: number | null;
  /**
   * input_source from latest assessment (primary observation provenance).
   * Distinct from latest_component_source (which may be "mixed"). Null when none.
   */
  latest_input_source: string | null;
  /** method_id from latest assessment; null when none. */
  latest_method_id: string | null;
  /** method_version from latest assessment; null when none. */
  latest_method_version: number | null;
  /** lookback_end_date from latest assessment (ISO date); null when none. */
  latest_lookback_end_date: string | null;
  /** lookback_start_date from latest assessment (ISO date); null when none. */
  latest_lookback_start_date: string | null;
  /** schema_version from latest assessment; null when none. */
  latest_schema_version: number | null;
  /** computed_at from latest assessment (ISO datetime); null when none. */
  latest_computed_at: string | null;
  /** event_time from latest assessment (ISO datetime); null when none. */
  latest_event_time: string | null;
  /**
   * probability_confidence from latest assessment when calibrated; null when none.
   * Distinct from latest_coverage_confidence.
   */
  latest_probability_confidence: number | null;
  detail: string;
}

export async function getResearchEvidenceSummary(
  baseUrl: string,
  symbol: string,
  options?: ApiRequestOptions,
): Promise<ResearchEvidenceSummary> {
  const url = `${baseUrl}/research/${encodeURIComponent(symbol)}/evidence-summary`;
  const { response, body } = await requestJson(url, undefined, options);
  if (!response.ok) {
    throw new ApiClientError(
      `Unexpected GET evidence-summary status: ${response.status}`,
      response.status,
      body,
    );
  }
  return body as ResearchEvidenceSummary;
}

/** Download the research evidence summary JSON attachment (Phase 24, ADR-0025). */
export async function downloadResearchEvidenceSummary(
  baseUrl: string,
  symbol: string,
  options?: ApiRequestOptions,
): Promise<string> {
  const url = `${baseUrl}/research/${encodeURIComponent(symbol)}/evidence-summary/export`;
  const headers = new Headers();
  if (options?.cookie) {
    headers.set("Cookie", options.cookie);
  }
  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }

  const response = await fetch(url, {
    headers,
    credentials: "include",
  });
  redirectToLoginIfNeeded(response.status, options);
  if (!response.ok) {
    const body = await readJson(response);
    throw new ApiClientError(
      `Unexpected GET evidence-summary export status: ${response.status}`,
      response.status,
      body,
    );
  }

  const blob = await response.blob();
  const filename =
    parseContentDispositionFilename(response.headers.get("Content-Disposition")) ??
    `aegis-${symbol.toUpperCase()}-evidence-summary.json`;

  if (typeof window !== "undefined") {
    const objectUrl = URL.createObjectURL(blob);
    try {
      const anchor = document.createElement("a");
      anchor.href = objectUrl;
      anchor.download = filename;
      anchor.rel = "noopener";
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
    } finally {
      URL.revokeObjectURL(objectUrl);
    }
  }

  return filename;
}

function parseContentDispositionFilename(header: string | null): string | null {
  if (!header) {
    return null;
  }
  const match = /filename="([^"]+)"/i.exec(header);
  return match?.[1] ?? null;
}

export function getApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
}
