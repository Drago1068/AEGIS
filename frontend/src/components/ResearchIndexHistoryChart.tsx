"use client";

import {
  ColorType,
  createChart,
  LineSeries,
  type IChartApi,
} from "lightweight-charts";
import { useEffect, useRef } from "react";

import type { ResearchAssessment } from "@/lib/api-client";
import { toResearchIndexHistoryChartData } from "@/lib/research-index-history-chart";

export type ResearchIndexHistoryChartProps = {
  symbol: string;
  assessments: ResearchAssessment[];
};

const CHART_HEIGHT = 220;

export function ResearchIndexHistoryChart({
  symbol,
  assessments,
}: ResearchIndexHistoryChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const points = toResearchIndexHistoryChartData(assessments);

  useEffect(() => {
    const container = containerRef.current;
    const seriesPoints = toResearchIndexHistoryChartData(assessments);
    if (!container || seriesPoints.length === 0) {
      return;
    }

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

    const series = chart.addSeries(LineSeries, {
      color: "#0f6e6e",
      lineWidth: 2,
      priceLineVisible: false,
      lastValueVisible: true,
    });
    series.setData(seriesPoints);
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
  }, [assessments]);

  if (points.length === 0) {
    return (
      <p
        className="mt-2 text-sm text-aegis-muted"
        data-testid="research-index-history-chart-empty"
      >
        No research_index chart points for {symbol}. Refresh history after assessments
        persist (research-only — not advice).
      </p>
    );
  }

  return (
    <div
      className="mt-2"
      data-testid="research-index-history-chart"
    >
      <p className="mb-1 text-xs text-aegis-muted">
        research_index vs as_of_trading_date (research-only — not advice)
      </p>
      <div
        ref={containerRef}
        className="w-full"
        role="img"
        aria-label={`${symbol} research_index history chart (research-only)`}
      />
    </div>
  );
}
