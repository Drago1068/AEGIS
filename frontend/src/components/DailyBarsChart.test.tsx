import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

class ResizeObserverStub {
  observe(): void {}
  unobserve(): void {}
  disconnect(): void {}
}

vi.stubGlobal("ResizeObserver", ResizeObserverStub);

const {
  setData,
  fitContent,
  applyOptions,
  remove,
  priceScaleApplyOptions,
  addSeries,
  createChart,
} = vi.hoisted(() => {
  const setDataFn = vi.fn();
  const fitContentFn = vi.fn();
  const applyOptionsFn = vi.fn();
  const removeFn = vi.fn();
  const priceScaleApplyOptionsFn = vi.fn();
  const addSeriesFn = vi.fn(() => ({
    setData: setDataFn,
    priceScale: () => ({ applyOptions: priceScaleApplyOptionsFn }),
  }));
  const createChartFn = vi.fn(() => ({
    addSeries: addSeriesFn,
    timeScale: () => ({ fitContent: fitContentFn }),
    applyOptions: applyOptionsFn,
    remove: removeFn,
  }));
  return {
    setData: setDataFn,
    fitContent: fitContentFn,
    applyOptions: applyOptionsFn,
    remove: removeFn,
    priceScaleApplyOptions: priceScaleApplyOptionsFn,
    addSeries: addSeriesFn,
    createChart: createChartFn,
  };
});

vi.mock("lightweight-charts", () => ({
  createChart,
  CandlestickSeries: { type: "Candlestick" },
  HistogramSeries: { type: "Histogram" },
  ColorType: { Solid: "solid" },
}));

import { DailyBarsChart } from "./DailyBarsChart";

describe("DailyBarsChart", () => {
  beforeEach(() => {
    setData.mockClear();
    fitContent.mockClear();
    applyOptions.mockClear();
    remove.mockClear();
    priceScaleApplyOptions.mockClear();
    addSeries.mockClear();
    createChart.mockClear();
  });

  it("renders an empty state when no bars are stored", () => {
    render(<DailyBarsChart symbol="AAPL" bars={[]} />);
    expect(screen.getByText(/no chart data for aapl/i)).toBeInTheDocument();
    expect(createChart).not.toHaveBeenCalled();
  });

  it("mounts a chart with an accessible name for sample bars", () => {
    render(
      <DailyBarsChart
        symbol="AAPL"
        bars={[
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
          {
            source: "alpha_vantage",
            symbol: "AAPL",
            trading_date: "2024-01-01",
            open: "98",
            high: "101",
            low: "97",
            close: "100",
            volume: 800,
            data_quality: "primary",
            schema_version: 1,
            ingested_at: "2024-01-01T12:00:00Z",
          },
        ]}
      />,
    );

    expect(screen.getByRole("img", { name: "AAPL daily OHLC chart" })).toBeInTheDocument();
    expect(createChart).toHaveBeenCalledTimes(1);
    expect(addSeries).toHaveBeenCalledTimes(2);
    expect(setData).toHaveBeenCalledTimes(2);
    expect(setData.mock.calls[0]?.[0]).toEqual([
      { time: "2024-01-01", open: 98, high: 101, low: 97, close: 100 },
      { time: "2024-01-02", open: 100, high: 110, low: 90, close: 105 },
    ]);
    expect(fitContent).toHaveBeenCalledTimes(1);
  });
});
