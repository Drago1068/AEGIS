import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { NoDataMessage } from "./NoDataMessage";

describe("NoDataMessage", () => {
  it("renders the Phase 0 placeholder state", () => {
    render(<NoDataMessage />);

    expect(screen.getByRole("heading", { name: /aegis 3\.0/i })).toBeInTheDocument();
    expect(screen.getByText(/no data yet/i)).toBeInTheDocument();
  });
});
