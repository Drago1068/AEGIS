import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { LoginForm } from "./LoginForm";

const replace = vi.fn();
const refresh = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    replace,
    refresh,
  }),
}));

vi.mock("@/lib/api-client", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api-client")>("@/lib/api-client");
  return {
    ...actual,
    getApiBaseUrl: () => "http://localhost:8000",
    login: vi.fn(),
  };
});

import { ApiClientError, login } from "@/lib/api-client";

describe("LoginForm", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows an error when login fails with 401", async () => {
    vi.mocked(login).mockRejectedValue(
      new ApiClientError("Unexpected POST /auth/login status: 401", 401, {
        detail: "invalid username or password",
      }),
    );

    const { container } = render(<LoginForm />);
    const form = container.querySelector("form");
    expect(form).not.toBeNull();

    fireEvent.change(screen.getByLabelText("Username"), { target: { value: "ops" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "wrong" } });
    fireEvent.submit(form!);

    expect(await screen.findByRole("alert")).toHaveTextContent(/invalid username or password/i);
    expect(login).toHaveBeenCalledWith("http://localhost:8000", "ops", "wrong");
    expect(replace).not.toHaveBeenCalled();
  });

  it("redirects to the console after a successful login", async () => {
    vi.mocked(login).mockResolvedValue({ username: "ops" });

    const { container } = render(<LoginForm />);
    const form = container.querySelector("form");
    expect(form).not.toBeNull();

    fireEvent.change(screen.getByLabelText("Username"), { target: { value: "ops" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "secret" } });
    fireEvent.submit(form!);

    await waitFor(() => {
      expect(login).toHaveBeenCalledWith("http://localhost:8000", "ops", "secret");
    });
    expect(replace).toHaveBeenCalledWith("/");
    expect(refresh).toHaveBeenCalled();
  });
});
