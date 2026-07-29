import { describe, expect, it } from "vitest";

import type { DailyBar } from "@/lib/api-client";
import { toDailyBarsChartData } from "./daily-bars-chart";

function bar(overrides: Partial<DailyBar> & Pick<DailyBar, "trading_date" | "open" | "close">): DailyBar {
  return {
    source: "alpha_vantage",
    symbol: "AAPL",
    high: "110",
    low: "90",
    volume: 1000,
    data_quality: "primary",
    schema_version: 1,
    ingested_at: "2024-01-02T12:00:00Z",
    ...overrides,
  };
}

describe("toDailyBarsChartData", () => {
  it("returns empty series for empty input", () => {
    expect(toDailyBarsChartData([])).toEqual({ candles: [], volumes: [] });
  });

  it("maps newest-first API bars to chronological candle and volume points", () => {
    const bars = [
      bar({ trading_date: "2024-01-03", open: "105", high: "112", low: "104", close: "110", volume: 3000 }),
      bar({ trading_date: "2024-01-02", open: "100", high: "108", low: "99", close: "105", volume: 2000 }),
      bar({ trading_date: "2024-01-01", open: "98", high: "101", low: "97", close: "100", volume: 1000 }),
    ];

    const { candles, volumes } = toDailyBarsChartData(bars);

    expect(candles.map((point) => point.time)).toEqual([
      "2024-01-01",
      "2024-01-02",
      "2024-01-03",
    ]);
    expect(candles[0]).toEqual({
      time: "2024-01-01",
      open: 98,
      high: 101,
      low: 97,
      close: 100,
    });
    expect(volumes.map((point) => point.value)).toEqual([1000, 2000, 3000]);
    expect(volumes[0]?.color).toMatch(/15, 110, 110/);
    expect(volumes[2]?.color).toMatch(/15, 110, 110/);
  });

  it("colors volume down when close is below open", () => {
    const { volumes } = toDailyBarsChartData([
      bar({ trading_date: "2024-01-02", open: "110", close: "100", volume: 500 }),
    ]);

    expect(volumes[0]?.color).toMatch(/155, 44, 44/);
  });
});
