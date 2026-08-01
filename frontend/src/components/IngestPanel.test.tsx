import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { IngestPanel } from "./IngestPanel";

vi.mock("@/lib/api-client", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api-client")>("@/lib/api-client");
  return {
    ...actual,
    getApiBaseUrl: () => "http://localhost:8000",
    ingestMarketData: vi.fn(),
  };
});

import { ingestMarketData } from "@/lib/api-client";

describe("IngestPanel", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("surfaces primary_fetch_fallback from ingest results", async () => {
    vi.mocked(ingestMarketData).mockResolvedValue({
      results: [
        {
          symbol: "AAPL",
          stored_count: 0,
          skipped_existing_count: 1,
          rejected_count: 0,
          rejections: {},
          error: null,
          latest_trading_date: "2026-07-31",
          latest_trading_date_source: "alpha_vantage",
          primary_latest_trading_date: "2026-07-31",
          primary_fetch_fallback: "full_to_compact",
        },
      ],
    });

    render(<IngestPanel />);
    fireEvent.click(screen.getByRole("button", { name: /run ingest/i }));

    await waitFor(() => {
      expect(screen.getByTestId("ingest-primary-fetch-fallback-AAPL")).toHaveTextContent(
        "full_to_compact",
      );
    });
  });

  it("shows em dash when primary_fetch_fallback is null", async () => {
    vi.mocked(ingestMarketData).mockResolvedValue({
      results: [
        {
          symbol: "AAPL",
          stored_count: 1,
          skipped_existing_count: 0,
          rejected_count: 0,
          rejections: {},
          error: null,
          latest_trading_date: "2026-07-31",
          latest_trading_date_source: "polygon",
          primary_latest_trading_date: "2026-07-31",
          primary_fetch_fallback: null,
        },
      ],
    });

    render(<IngestPanel />);
    fireEvent.click(screen.getByRole("button", { name: /run ingest/i }));

    await waitFor(() => {
      expect(screen.getByTestId("ingest-primary-fetch-fallback-AAPL")).toHaveTextContent("—");
    });
  });
});
