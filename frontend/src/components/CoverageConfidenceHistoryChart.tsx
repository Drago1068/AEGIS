"use client";

import {
  ColorType,
  createChart,
  LineSeries,
  type IChartApi,
} from "lightweight-charts";
import { useEffect, useRef } from "react";

import type { ResearchAssessment } from "@/lib/api-client";
import { toCoverageConfidenceHistoryChartData } from "@/lib/coverage-confidence-history-chart";

export type CoverageConfidenceHistoryChartProps = {
  symbol: string;
  assessments: ResearchAssessment[];
};

const CHART_HEIGHT = 220;

export function CoverageConfidenceHistoryChart({
  symbol,
  assessments,
}: CoverageConfidenceHistoryChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const points = toCoverageConfidenceHistoryChartData(assessments);

  useEffect(() => {
    const container = containerRef.current;
    const seriesPoints = toCoverageConfidenceHistoryChartData(assessments);
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
      color: "#3d5a6c",
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
        data-testid="coverage-confidence-history-chart-empty"
      >
        No coverage_confidence chart points for {symbol}. Distinct from probability
        confidence (research-only — not advice).
      </p>
    );
  }

  return (
    <div className="mt-2" data-testid="coverage-confidence-history-chart">
      <p className="mb-1 text-xs text-aegis-muted">
        coverage_confidence vs as_of_trading_date (distinct from probability; research-only
        — not advice)
      </p>
      <div
        ref={containerRef}
        className="w-full"
        role="img"
        aria-label={`${symbol} coverage_confidence history chart (research-only)`}
      />
    </div>
  );
}
