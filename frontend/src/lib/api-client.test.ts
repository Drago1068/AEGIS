import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  ApiClientError,
  addWatchlistSymbol,
  getHealth,
  getMe,
  getReady,
  ingestMarketData,
  listDailyBars,
  listWatchlist,
  login,
  logout,
  removeWatchlistSymbol,
} from "./api-client";

function mockFetch(payload: {
  ok?: boolean;
  status: number;
  json?: unknown;
}): ReturnType<typeof vi.fn> {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: payload.ok ?? (payload.status >= 200 && payload.status < 300),
    status: payload.status,
    json: async () => payload.json ?? null,
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

describe("getHealth", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns a typed payload matching the backend /health contract", async () => {
    mockFetch({ status: 200, json: { status: "ok" } });
    await expect(getHealth("http://localhost:8000")).resolves.toEqual({ status: "ok" });
  });

  it("throws when the backend responds with a non-ok status", async () => {
    mockFetch({ status: 503, json: {} });
    await expect(getHealth("http://localhost:8000")).rejects.toThrow(ApiClientError);
  });
});

describe("getReady", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns ok:true with the ready payload on HTTP 200", async () => {
    mockFetch({
      status: 200,
      json: { status: "ready", checks: { database: "ok", redis: "ok" } },
    });
    await expect(getReady("http://localhost:8000")).resolves.toEqual({
      ok: true,
      body: { status: "ready", checks: { database: "ok", redis: "ok" } },
    });
  });

  it("returns ok:false with the typed error payload on HTTP 503", async () => {
    mockFetch({
      status: 503,
      json: {
        status: "unavailable",
        checks: { database: "unavailable", redis: "ok" },
      },
    });
    await expect(getReady("http://localhost:8000")).resolves.toEqual({
      ok: false,
      body: {
        status: "unavailable",
        checks: { database: "unavailable", redis: "ok" },
      },
    });
  });
});

describe("auth client", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("logs in with credentials include and does not redirect on 401", async () => {
    const assign = vi.fn();
    vi.stubGlobal("location", { pathname: "/", assign });
    const fetchMock = mockFetch({ status: 401, json: { detail: "invalid username or password" } });

    await expect(login("http://localhost:8000", "ops", "bad")).rejects.toMatchObject({
      status: 401,
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/auth/login",
      expect.objectContaining({
        method: "POST",
        credentials: "include",
      }),
    );
    expect(assign).not.toHaveBeenCalled();
  });

  it("returns the operator identity on successful login", async () => {
    mockFetch({ status: 200, json: { username: "ops" } });
    await expect(login("http://localhost:8000", "ops", "secret")).resolves.toEqual({
      username: "ops",
    });
  });

  it("calls logout with credentials include", async () => {
    const fetchMock = mockFetch({ status: 204, json: null });
    await expect(logout("http://localhost:8000")).resolves.toBeUndefined();
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/auth/logout",
      expect.objectContaining({
        method: "POST",
        credentials: "include",
      }),
    );
  });

  it("calls getMe with credentials include", async () => {
    const fetchMock = mockFetch({ status: 200, json: { username: "ops" } });
    await expect(getMe("http://localhost:8000")).resolves.toEqual({ username: "ops" });
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/auth/me",
      expect.objectContaining({
        credentials: "include",
      }),
    );
  });
});

describe("401 handling", () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("redirects to /login on 401 for protected calls when not already on login", async () => {
    const assign = vi.fn();
    vi.stubGlobal("location", { pathname: "/", assign });
    mockFetch({ status: 401, json: { detail: "unauthorized" } });

    await expect(listWatchlist("http://localhost:8000")).rejects.toMatchObject({ status: 401 });
    expect(assign).toHaveBeenCalledWith("/login");
  });

  it("does not redirect on 401 when already on the login page", async () => {
    const assign = vi.fn();
    vi.stubGlobal("location", { pathname: "/login", assign });
    mockFetch({ status: 401, json: { detail: "unauthorized" } });

    await expect(getMe("http://localhost:8000")).rejects.toMatchObject({ status: 401 });
    expect(assign).not.toHaveBeenCalled();
  });

  it("does not redirect on 401 when skipAuthRedirect is set", async () => {
    const assign = vi.fn();
    vi.stubGlobal("location", { pathname: "/", assign });
    mockFetch({ status: 401, json: { detail: "unauthorized" } });

    await expect(
      getMe("http://localhost:8000", { skipAuthRedirect: true }),
    ).rejects.toMatchObject({ status: 401 });
    expect(assign).not.toHaveBeenCalled();
  });
});

describe("credentials include", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("sends credentials include for watchlist and market-data calls", async () => {
    const fetchMock = mockFetch({
      status: 200,
      json: [],
    });

    await listWatchlist("http://localhost:8000");
    expect(fetchMock).toHaveBeenLastCalledWith(
      "http://localhost:8000/watchlist",
      expect.objectContaining({ credentials: "include" }),
    );

    await addWatchlistSymbol("http://localhost:8000", "AAPL");
    expect(fetchMock).toHaveBeenLastCalledWith(
      "http://localhost:8000/watchlist",
      expect.objectContaining({
        method: "POST",
        credentials: "include",
      }),
    );

    mockFetch({ status: 204, json: null });
    const deleteFetch = vi.mocked(fetch);
    await removeWatchlistSymbol("http://localhost:8000", "AAPL");
    expect(deleteFetch).toHaveBeenLastCalledWith(
      "http://localhost:8000/watchlist/AAPL",
      expect.objectContaining({
        method: "DELETE",
        credentials: "include",
      }),
    );

    mockFetch({ status: 200, json: [] });
    const barsFetch = vi.mocked(fetch);
    await listDailyBars("http://localhost:8000", "AAPL");
    expect(barsFetch).toHaveBeenLastCalledWith(
      "http://localhost:8000/market-data/AAPL/daily-bars?limit=100",
      expect.objectContaining({ credentials: "include" }),
    );

    mockFetch({
      status: 200,
      json: { results: [] },
    });
    const ingestFetch = vi.mocked(fetch);
    await ingestMarketData("http://localhost:8000");
    expect(ingestFetch).toHaveBeenLastCalledWith(
      "http://localhost:8000/market-data/ingest",
      expect.objectContaining({
        method: "POST",
        credentials: "include",
      }),
    );
  });

  it("forwards a Cookie header when provided for SSR", async () => {
    const fetchMock = mockFetch({ status: 200, json: { username: "ops" } });
    await getMe("http://localhost:8000", {
      cookie: "aegis_session=abc",
      skipAuthRedirect: true,
    });

    const init = fetchMock.mock.calls[0]?.[1] as RequestInit;
    const headers = new Headers(init.headers);
    expect(headers.get("Cookie")).toBe("aegis_session=abc");
    expect(init.credentials).toBe("include");
  });
});

describe("watchlist client", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("lists watchlist symbols", async () => {
    mockFetch({
      status: 200,
      json: [
        {
          symbol: "AAPL",
          is_active: true,
          created_at: "2024-01-01T00:00:00Z",
          updated_at: "2024-01-01T00:00:00Z",
        },
      ],
    });
    const rows = await listWatchlist("http://localhost:8000");
    expect(rows).toHaveLength(1);
    expect(rows[0]?.symbol).toBe("AAPL");
  });

  it("adds a watchlist symbol", async () => {
    mockFetch({
      status: 201,
      json: {
        symbol: "TSLA",
        is_active: true,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      },
    });
    const row = await addWatchlistSymbol("http://localhost:8000", "tsla");
    expect(row.symbol).toBe("TSLA");
  });

  it("surfaces 422 when adding an invalid symbol", async () => {
    mockFetch({ status: 422, json: { detail: "invalid" } });
    await expect(addWatchlistSymbol("http://localhost:8000", "!!!")).rejects.toMatchObject({
      status: 422,
    });
  });

  it("removes a watchlist symbol", async () => {
    mockFetch({ status: 204, json: null });
    await expect(removeWatchlistSymbol("http://localhost:8000", "AAPL")).resolves.toBeUndefined();
  });
});

describe("market data client", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("lists daily bars", async () => {
    mockFetch({
      status: 200,
      json: [
        {
          source: "alpha_vantage",
          symbol: "AAPL",
          trading_date: "2024-01-02",
          open: "100",
          high: "110",
          low: "90",
          close: "105",
          volume: 1000,
          data_quality: "primary",
          schema_version: 1,
          ingested_at: "2024-01-02T12:00:00Z",
        },
      ],
    });
    const bars = await listDailyBars("http://localhost:8000", "AAPL");
    expect(bars[0]?.close).toBe("105");
  });

  it("throws ApiClientError on 404 for unknown symbol bars", async () => {
    mockFetch({ status: 404, json: { detail: "missing" } });
    await expect(listDailyBars("http://localhost:8000", "UNKNOWN")).rejects.toMatchObject({
      status: 404,
    });
  });

  it("returns ingest run summary", async () => {
    mockFetch({
      status: 200,
      json: {
        results: [
          {
            symbol: "AAPL",
            stored_count: 1,
            skipped_existing_count: 0,
            rejected_count: 0,
            rejections: {},
            error: null,
          },
        ],
      },
    });
    const run = await ingestMarketData("http://localhost:8000");
    expect(run.results[0]?.stored_count).toBe(1);
  });

  it("throws on non-ok ingest", async () => {
    mockFetch({ status: 500, json: { detail: "boom" } });
    await expect(ingestMarketData("http://localhost:8000")).rejects.toThrow(ApiClientError);
  });
});

describe("downloadResearchEvidenceSummary", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("downloads the export attachment and returns the filename", async () => {
    const { downloadResearchEvidenceSummary } = await import("./api-client");
    const blob = new Blob(['{"state":"research_only"}'], { type: "application/json" });
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: {
        get: (name: string) =>
          name.toLowerCase() === "content-disposition"
            ? 'attachment; filename="aegis-AAPL-evidence-summary.json"'
            : null,
      },
      blob: async () => blob,
      json: async () => null,
    });
    vi.stubGlobal("fetch", fetchMock);
    const createObjectURL = vi.fn(() => "blob:mock");
    const revokeObjectURL = vi.fn();
    vi.stubGlobal("URL", { createObjectURL, revokeObjectURL });
    const click = vi.fn();
    const remove = vi.fn();
    const appendChild = vi.spyOn(document.body, "appendChild").mockImplementation((node) => node);
    vi.spyOn(document, "createElement").mockReturnValue({
      href: "",
      download: "",
      rel: "",
      click,
      remove,
    } as unknown as HTMLAnchorElement);

    await expect(
      downloadResearchEvidenceSummary("http://localhost:8000", "AAPL"),
    ).resolves.toBe("aegis-AAPL-evidence-summary.json");

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/research/AAPL/evidence-summary/export",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(click).toHaveBeenCalled();
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:mock");
    appendChild.mockRestore();
  });

  it("throws ApiClientError on non-ok export", async () => {
    const { downloadResearchEvidenceSummary } = await import("./api-client");
    mockFetch({ status: 401, json: { detail: "unauthorized" } });
    await expect(
      downloadResearchEvidenceSummary("http://localhost:8000", "AAPL", {
        skipAuthRedirect: true,
      }),
    ).rejects.toMatchObject({ status: 401 });
  });
});

describe("downloadCalibrationReadiness", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("downloads the readiness export attachment and returns the filename", async () => {
    const { downloadCalibrationReadiness } = await import("./api-client");
    const blob = new Blob(['{"status":"ready"}'], { type: "application/json" });
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: {
        get: (name: string) =>
          name.toLowerCase() === "content-disposition"
            ? 'attachment; filename="aegis-AAPL-calibration-readiness.json"'
            : null,
      },
      blob: async () => blob,
      json: async () => null,
    });
    vi.stubGlobal("fetch", fetchMock);
    const createObjectURL = vi.fn(() => "blob:mock");
    const revokeObjectURL = vi.fn();
    vi.stubGlobal("URL", { createObjectURL, revokeObjectURL });
    const click = vi.fn();
    const remove = vi.fn();
    vi.spyOn(document.body, "appendChild").mockImplementation((node) => node);
    vi.spyOn(document, "createElement").mockReturnValue({
      href: "",
      download: "",
      rel: "",
      click,
      remove,
    } as unknown as HTMLAnchorElement);

    await expect(
      downloadCalibrationReadiness("http://localhost:8000", "AAPL"),
    ).resolves.toBe("aegis-AAPL-calibration-readiness.json");

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/research/AAPL/calibration-readiness/export",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(click).toHaveBeenCalled();
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:mock");
  });
});
