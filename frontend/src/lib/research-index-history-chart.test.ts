import { describe, expect, it } from "vitest";

import { toResearchIndexHistoryChartData } from "./research-index-history-chart";

describe("toResearchIndexHistoryChartData", () => {
  it("returns empty series for empty input", () => {
    expect(toResearchIndexHistoryChartData([])).toEqual([]);
  });

  it("maps newest-first assessments to chronological research_index points", () => {
    const points = toResearchIndexHistoryChartData([
      {
        as_of_trading_date: "2024-01-03",
        components: { research_index: 0.5 },
      },
      {
        as_of_trading_date: "2024-01-02",
        components: { research_index: 0.4 },
      },
      {
        as_of_trading_date: "2024-01-01",
        components: { research_index: 0.3 },
      },
    ]);

    expect(points).toEqual([
      { time: "2024-01-01", value: 0.3 },
      { time: "2024-01-02", value: 0.4 },
      { time: "2024-01-03", value: 0.5 },
    ]);
  });

  it("skips non-finite research_index and invalid dates (fail-closed)", () => {
    const points = toResearchIndexHistoryChartData([
      { as_of_trading_date: "2024-01-03", components: { research_index: Number.NaN } },
      { as_of_trading_date: "not-a-date", components: { research_index: 0.9 } },
      { as_of_trading_date: "2024-01-02", components: { research_index: 0.4 } },
      { as_of_trading_date: "2024-01-01", components: {} },
    ]);

    expect(points).toEqual([{ time: "2024-01-02", value: 0.4 }]);
  });

  it("keeps the newest research_index when as_of dates collide", () => {
    const points = toResearchIndexHistoryChartData([
      { as_of_trading_date: "2024-01-02", components: { research_index: 0.8 } },
      { as_of_trading_date: "2024-01-02", components: { research_index: 0.1 } },
      { as_of_trading_date: "2024-01-01", components: { research_index: 0.2 } },
    ]);

    expect(points).toEqual([
      { time: "2024-01-01", value: 0.2 },
      { time: "2024-01-02", value: 0.8 },
    ]);
  });
});
