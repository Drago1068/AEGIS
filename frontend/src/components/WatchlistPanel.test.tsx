import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { WatchlistPanel } from "./WatchlistPanel";

vi.mock("next/link", () => ({
  default: ({
    href,
    children,
    className,
  }: {
    href: string;
    children: React.ReactNode;
    className?: string;
  }) => (
    <a href={href} className={className}>
      {children}
    </a>
  ),
}));

vi.mock("@/lib/api-client", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api-client")>("@/lib/api-client");
  return {
    ...actual,
    getApiBaseUrl: () => "http://localhost:8000",
    addWatchlistSymbol: vi.fn(),
    removeWatchlistSymbol: vi.fn(),
  };
});

import { addWatchlistSymbol, removeWatchlistSymbol } from "@/lib/api-client";

describe("WatchlistPanel", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders initial symbols and links to the bars page", () => {
    render(
      <WatchlistPanel
        initialSymbols={[
          {
            symbol: "AAPL",
            is_active: true,
            created_at: "2024-01-01T00:00:00Z",
            updated_at: "2024-01-01T00:00:00Z",
          },
        ]}
      />,
    );

    expect(screen.getByRole("link", { name: "AAPL" })).toHaveAttribute("href", "/symbols/AAPL");
  });

  it("shows empty state when there are no symbols", () => {
    render(<WatchlistPanel initialSymbols={[]} />);
    expect(screen.getByText(/no active symbols/i)).toBeInTheDocument();
  });

  it("adds a symbol through the form", async () => {
    vi.mocked(addWatchlistSymbol).mockResolvedValue({
      symbol: "MSFT",
      is_active: true,
      created_at: "2024-01-01T00:00:00Z",
      updated_at: "2024-01-01T00:00:00Z",
    });

    const { container } = render(<WatchlistPanel initialSymbols={[]} />);
    const form = container.querySelector("form");
    expect(form).not.toBeNull();
    fireEvent.change(screen.getByLabelText("Symbol"), { target: { value: "msft" } });
    fireEvent.submit(form!);

    await waitFor(() => {
      expect(addWatchlistSymbol).toHaveBeenCalledWith("http://localhost:8000", "msft");
    });
    expect(await screen.findByRole("link", { name: "MSFT" })).toBeInTheDocument();
  });

  it("removes a symbol", async () => {
    vi.mocked(removeWatchlistSymbol).mockResolvedValue(undefined);

    render(
      <WatchlistPanel
        initialSymbols={[
          {
            symbol: "AAPL",
            is_active: true,
            created_at: "2024-01-01T00:00:00Z",
            updated_at: "2024-01-01T00:00:00Z",
          },
        ]}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "Remove" }));
    await waitFor(() => {
      expect(removeWatchlistSymbol).toHaveBeenCalledWith("http://localhost:8000", "AAPL");
    });
    expect(await screen.findByText(/no active symbols/i)).toBeInTheDocument();
  });
});
