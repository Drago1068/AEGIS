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
  symbol: string;
  method_id: string;
  method_version: number;
  state: string;
  as_of_trading_date: string;
  event_time: string;
  computed_at: string;
  coverage_confidence: number;
  /** Always null in Phase 6 (not calibrated). Never merge with coverage_confidence. */
  probability_confidence: number | null;
  components: {
    total_return_20: number;
    realized_vol_20: number;
    research_index: number;
    [key: string]: number;
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

export async function listResearchAssessments(
  baseUrl: string,
  symbol: string,
  limit = 20,
  options?: ApiRequestOptions,
): Promise<ResearchAssessment[]> {
  const url =
    `${baseUrl}/research/${encodeURIComponent(symbol)}/assessments` +
    `?limit=${limit}`;
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

export function getApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
}
