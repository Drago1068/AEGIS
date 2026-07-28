import { afterEach, describe, expect, it, vi } from "vitest";

import {
  ApiClientError,
  addWatchlistSymbol,
  getHealth,
  getReady,
  ingestMarketData,
  listDailyBars,
  listWatchlist,
  removeWatchlistSymbol,
} from "./api-client";

function mockFetch(payload: {
  ok?: boolean;
  status: number;
  json?: unknown;
}): void {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: payload.ok ?? (payload.status >= 200 && payload.status < 300),
      status: payload.status,
      json: async () => payload.json ?? null,
    }),
  );
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
