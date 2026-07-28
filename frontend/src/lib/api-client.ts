/**
 * Typed HTTP client for the AEGIS backend API.
 *
 * Types here must stay in sync with the backend's Pydantic response schemas
 * (`backend/src/aegis/api/schemas/health.py`). Phase 0 only exposes liveness/readiness.
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

export async function getHealth(baseUrl: string): Promise<HealthResponse> {
  const response = await fetch(`${baseUrl}/health`);
  if (!response.ok) {
    throw new Error(`Unexpected /health status: ${response.status}`);
  }
  return (await response.json()) as HealthResponse;
}

export async function getReady(
  baseUrl: string,
): Promise<{ ok: true; body: ReadyResponse } | { ok: false; body: NotReadyResponse }> {
  const response = await fetch(`${baseUrl}/ready`);
  const body = await response.json();
  if (response.status === 200) {
    return { ok: true, body: body as ReadyResponse };
  }
  return { ok: false, body: body as NotReadyResponse };
}
