import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { DailyBarsTable } from "./DailyBarsTable";

describe("DailyBarsTable", () => {
  it("renders an empty state when no bars are stored", () => {
    render(<DailyBarsTable symbol="AAPL" bars={[]} />);
    expect(screen.getByText(/no stored daily bars for aapl/i)).toBeInTheDocument();
  });

  it("renders bar rows", () => {
    render(
      <DailyBarsTable
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
        ]}
      />,
    );

    expect(screen.getByText("2024-01-02")).toBeInTheDocument();
    expect(screen.getByText("105")).toBeInTheDocument();
    expect(screen.getByText("1000")).toBeInTheDocument();
  });
});
