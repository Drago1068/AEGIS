import { afterEach, describe, expect, it, vi } from "vitest";

import { getHealth, getReady } from "./api-client";

describe("getHealth", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns a typed payload matching the backend /health contract", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ status: "ok" }),
      }),
    );

    const result = await getHealth("http://localhost:8000");

    expect(result).toEqual({ status: "ok" });
  });

  it("throws when the backend responds with a non-ok status", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, status: 503, json: async () => ({}) }),
    );

    await expect(getHealth("http://localhost:8000")).rejects.toThrow();
  });
});

describe("getReady", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns ok:true with the ready payload on HTTP 200", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        status: 200,
        json: async () => ({ status: "ready", checks: { database: "ok", redis: "ok" } }),
      }),
    );

    const result = await getReady("http://localhost:8000");

    expect(result).toEqual({
      ok: true,
      body: { status: "ready", checks: { database: "ok", redis: "ok" } },
    });
  });

  it("returns ok:false with the typed error payload on HTTP 503", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        status: 503,
        json: async () => ({
          status: "unavailable",
          checks: { database: "unavailable", redis: "ok" },
        }),
      }),
    );

    const result = await getReady("http://localhost:8000");

    expect(result).toEqual({
      ok: false,
      body: { status: "unavailable", checks: { database: "unavailable", redis: "ok" } },
    });
  });
});
