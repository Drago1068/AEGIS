"use client";

import {
  CandlestickSeries,
  ColorType,
  createChart,
  HistogramSeries,
  type IChartApi,
} from "lightweight-charts";
import { useEffect, useRef } from "react";

import { DailyBar } from "@/lib/api-client";
import { toDailyBarsChartData } from "@/lib/daily-bars-chart";

type DailyBarsChartProps = {
  symbol: string;
  bars: DailyBar[];
};

const CHART_HEIGHT = 360;

export function DailyBarsChart({ symbol, bars }: DailyBarsChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container || bars.length === 0) {
      return;
    }

    const { candles, volumes } = toDailyBarsChartData(bars);
    let chart: IChartApi | null = createChart(container, {
      width: container.clientWidth,
      height: CHART_HEIGHT,
      layout: {
        background: { type: ColorType.Solid, color: "#ffffff" },
        textColor: "#5b6b76",
        fontFamily: "var(--font-sans)",
      },
      grid: {
        vertLines: { color: "#d5dde3" },
        horzLines: { color: "#d5dde3" },
      },
      rightPriceScale: {
        borderColor: "#d5dde3",
      },
      timeScale: {
        borderColor: "#d5dde3",
      },
      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
        horzTouchDrag: true,
        vertTouchDrag: true,
      },
      handleScale: {
        axisPressedMouseMove: true,
        mouseWheel: true,
        pinch: true,
      },
    });

    const candleSeries = chart.addSeries(
      CandlestickSeries,
      {
        upColor: "#0f6e6e",
        downColor: "#9b2c2c",
        borderUpColor: "#0f6e6e",
        borderDownColor: "#9b2c2c",
        wickUpColor: "#0f6e6e",
        wickDownColor: "#9b2c2c",
      },
      0,
    );
    candleSeries.setData(candles);

    const volumeSeries = chart.addSeries(
      HistogramSeries,
      {
        priceFormat: { type: "volume" },
      },
      1,
    );
    volumeSeries.priceScale().applyOptions({
      scaleMargins: { top: 0.1, bottom: 0 },
    });
    volumeSeries.setData(volumes);

    chart.timeScale().fitContent();

    const resizeObserver = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (!entry || !chart) {
        return;
      }
      chart.applyOptions({ width: entry.contentRect.width });
    });
    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
      chart?.remove();
      chart = null;
    };
  }, [bars]);

  if (bars.length === 0) {
    return (
      <p className="text-sm text-aegis-muted">
        No chart data for {symbol}. Run ingest after adding the symbol to the watchlist.
      </p>
    );
  }

  return (
    <div
      ref={containerRef}
      className="w-full"
      role="img"
      aria-label={`${symbol} daily OHLC chart`}
    />
  );
}
