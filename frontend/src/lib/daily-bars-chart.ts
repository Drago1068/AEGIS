/**
 * Adapters for rendering stored daily bars with TradingView Lightweight Charts.
 *
 * The API returns bars newest-first; the chart library requires chronological
 * (oldest-first) series data. See ADR-0006.
 */

import type { DailyBar } from "@/lib/api-client";

export type CandlestickPoint = {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
};

export type VolumePoint = {
  time: string;
  value: number;
  color: string;
};

export type DailyBarsChartData = {
  candles: CandlestickPoint[];
  volumes: VolumePoint[];
};

const UP_VOLUME_COLOR = "rgba(15, 110, 110, 0.5)";
const DOWN_VOLUME_COLOR = "rgba(155, 44, 44, 0.5)";

function parsePrice(value: string): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    throw new Error(`Invalid OHLC price value: ${value}`);
  }
  return parsed;
}

/**
 * Map API daily bars (newest-first) to chronological candle and volume series.
 */
export function toDailyBarsChartData(bars: DailyBar[]): DailyBarsChartData {
  const chronological = [...bars].reverse();
  const candles: CandlestickPoint[] = [];
  const volumes: VolumePoint[] = [];

  for (const bar of chronological) {
    const open = parsePrice(bar.open);
    const high = parsePrice(bar.high);
    const low = parsePrice(bar.low);
    const close = parsePrice(bar.close);
    candles.push({
      time: bar.trading_date,
      open,
      high,
      low,
      close,
    });
    volumes.push({
      time: bar.trading_date,
      value: bar.volume,
      color: close >= open ? UP_VOLUME_COLOR : DOWN_VOLUME_COLOR,
    });
  }

  return { candles, volumes };
}
