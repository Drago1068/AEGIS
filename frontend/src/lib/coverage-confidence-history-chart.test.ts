import { describe, expect, it } from "vitest";

import { toCoverageConfidenceHistoryChartData } from "./coverage-confidence-history-chart";

describe("toCoverageConfidenceHistoryChartData", () => {
  it("returns empty series for empty input", () => {
    expect(toCoverageConfidenceHistoryChartData([])).toEqual([]);
  });

  it("maps newest-first assessments to chronological coverage_confidence points", () => {
    const points = toCoverageConfidenceHistoryChartData([
      { as_of_trading_date: "2024-01-03", coverage_confidence: 0.95 },
      { as_of_trading_date: "2024-01-02", coverage_confidence: 0.9 },
      { as_of_trading_date: "2024-01-01", coverage_confidence: 0.85 },
    ]);

    expect(points).toEqual([
      { time: "2024-01-01", value: 0.85 },
      { time: "2024-01-02", value: 0.9 },
      { time: "2024-01-03", value: 0.95 },
    ]);
  });

  it("skips non-finite coverage_confidence and invalid dates (fail-closed)", () => {
    const points = toCoverageConfidenceHistoryChartData([
      { as_of_trading_date: "2024-01-03", coverage_confidence: Number.NaN },
      { as_of_trading_date: "not-a-date", coverage_confidence: 0.99 },
      { as_of_trading_date: "2024-01-02", coverage_confidence: 0.9 },
      { as_of_trading_date: "2024-01-01" },
    ]);

    expect(points).toEqual([{ time: "2024-01-02", value: 0.9 }]);
  });

  it("keeps the newest coverage_confidence when as_of dates collide", () => {
    const points = toCoverageConfidenceHistoryChartData([
      { as_of_trading_date: "2024-01-02", coverage_confidence: 0.99 },
      { as_of_trading_date: "2024-01-02", coverage_confidence: 0.1 },
      { as_of_trading_date: "2024-01-01", coverage_confidence: 0.8 },
    ]);

    expect(points).toEqual([
      { time: "2024-01-01", value: 0.8 },
      { time: "2024-01-02", value: 0.99 },
    ]);
  });

  it("does not invent coverage from probability_confidence", () => {
    const row = {
      as_of_trading_date: "2024-01-01",
      probability_confidence: 0.62,
    };
    expect(toCoverageConfidenceHistoryChartData([row])).toEqual([]);
  });
});
