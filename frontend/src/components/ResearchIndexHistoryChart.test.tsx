import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

class ResizeObserverStub {
  observe(): void {}
  unobserve(): void {}
  disconnect(): void {}
}

vi.stubGlobal("ResizeObserver", ResizeObserverStub);

const { setData, fitContent, addSeries, createChart, remove } = vi.hoisted(() => {
  const setDataFn = vi.fn();
  const fitContentFn = vi.fn();
  const removeFn = vi.fn();
  const addSeriesFn = vi.fn(() => ({
    setData: setDataFn,
  }));
  const createChartFn = vi.fn(() => ({
    addSeries: addSeriesFn,
    timeScale: () => ({ fitContent: fitContentFn }),
    applyOptions: vi.fn(),
    remove: removeFn,
  }));
  return {
    setData: setDataFn,
    fitContent: fitContentFn,
    addSeries: addSeriesFn,
    createChart: createChartFn,
    remove: removeFn,
  };
});

vi.mock("lightweight-charts", () => ({
  createChart,
  LineSeries: { type: "Line" },
  ColorType: { Solid: "solid" },
}));

import type { ResearchAssessment } from "@/lib/api-client";

import { ResearchIndexHistoryChart } from "./ResearchIndexHistoryChart";

function assessment(
  asOf: string,
  researchIndex: number,
): ResearchAssessment {
  return {
    id: 1,
    symbol: "AAPL",
    method_id: "daily_bar_research_v1",
    method_version: 1,
    state: "research_only",
    as_of_trading_date: asOf,
    event_time: `${asOf}T23:59:59Z`,
    computed_at: `${asOf}T18:00:00Z`,
    coverage_confidence: 0.9,
    probability_confidence: null,
    components: {
      total_return_20: 0.1,
      realized_vol_20: 0.2,
      research_index: researchIndex,
    },
    schema_version: 1,
    input_source: "alpha_vantage",
    lookback_start_date: "2023-12-01",
    lookback_end_date: asOf,
    bar_count: 20,
  };
}

describe("ResearchIndexHistoryChart", () => {
  beforeEach(() => {
    setData.mockClear();
    fitContent.mockClear();
    addSeries.mockClear();
    createChart.mockClear();
    remove.mockClear();
  });

  it("renders an empty state when no chartable points exist", () => {
    render(<ResearchIndexHistoryChart symbol="AAPL" assessments={[]} />);
    expect(screen.getByTestId("research-index-history-chart-empty")).toHaveTextContent(
      /no research_index chart points for aapl/i,
    );
    expect(createChart).not.toHaveBeenCalled();
  });

  it("mounts a research-only chart from assessment history", () => {
    render(
      <ResearchIndexHistoryChart
        symbol="AAPL"
        assessments={[assessment("2024-01-02", 0.46), assessment("2024-01-01", 0.4)]}
      />,
    );

    expect(screen.getByTestId("research-index-history-chart")).toBeInTheDocument();
    expect(
      screen.getByRole("img", {
        name: "AAPL research_index history chart (research-only)",
      }),
    ).toBeInTheDocument();
    expect(createChart).toHaveBeenCalledTimes(1);
    expect(addSeries).toHaveBeenCalledTimes(1);
    expect(setData).toHaveBeenCalledWith([
      { time: "2024-01-01", value: 0.4 },
      { time: "2024-01-02", value: 0.46 },
    ]);
    expect(fitContent).toHaveBeenCalledTimes(1);
  });
});
