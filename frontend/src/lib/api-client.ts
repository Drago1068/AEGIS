/**
 * Typed HTTP client for the AEGIS backend API.
 *
 * Types here must stay in sync with the backend's Pydantic response schemas under
 * `backend/src/aegis/api/schemas/`. See ADR-0004 for the Phase 3 operator console contract.
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

async function requestJson(
  url: string,
  init?: RequestInit,
): Promise<{ response: Response; body: unknown }> {
  const response = await fetch(url, init);
  const body = await readJson(response);
  return { response, body };
}

export async function getHealth(baseUrl: string): Promise<HealthResponse> {
  const { response, body } = await requestJson(`${baseUrl}/health`);
  if (!response.ok) {
    throw new ApiClientError(`Unexpected /health status: ${response.status}`, response.status, body);
  }
  return body as HealthResponse;
}

export async function getReady(
  baseUrl: string,
): Promise<{ ok: true; body: ReadyResponse } | { ok: false; body: NotReadyResponse }> {
  const { response, body } = await requestJson(`${baseUrl}/ready`);
  if (response.status === 200) {
    return { ok: true, body: body as ReadyResponse };
  }
  return { ok: false, body: body as NotReadyResponse };
}

export async function listWatchlist(baseUrl: string): Promise<WatchlistSymbol[]> {
  const { response, body } = await requestJson(`${baseUrl}/watchlist`);
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
): Promise<WatchlistSymbol> {
  const { response, body } = await requestJson(`${baseUrl}/watchlist`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ symbol }),
  });
  if (!response.ok) {
    throw new ApiClientError(
      `Unexpected POST /watchlist status: ${response.status}`,
      response.status,
      body,
    );
  }
  return body as WatchlistSymbol;
}

export async function removeWatchlistSymbol(baseUrl: string, symbol: string): Promise<void> {
  const { response, body } = await requestJson(
    `${baseUrl}/watchlist/${encodeURIComponent(symbol)}`,
    { method: "DELETE" },
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
): Promise<DailyBar[]> {
  const url = `${baseUrl}/market-data/${encodeURIComponent(symbol)}/daily-bars?limit=${limit}`;
  const { response, body } = await requestJson(url);
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

export async function ingestMarketData(baseUrl: string): Promise<IngestionRunResponse> {
  const { response, body } = await requestJson(`${baseUrl}/market-data/ingest`, {
    method: "POST",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new ApiClientError(
      `Unexpected POST /market-data/ingest status: ${response.status}`,
      response.status,
      body,
    );
  }
  return body as IngestionRunResponse;
}

export function getApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
}
