"use client";

import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";
import type { FormEvent } from "react";

import { ApiClientError, getApiBaseUrl, login } from "@/lib/api-client";

export function LoginForm() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const baseUrl = getApiBaseUrl();

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const user = username.trim();
    if (!user || !password) {
      setError("Enter a username and password.");
      return;
    }

    startTransition(async () => {
      setError(null);
      try {
        await login(baseUrl, user, password);
        router.replace("/");
        router.refresh();
      } catch (err) {
        if (err instanceof ApiClientError && err.status === 401) {
          setError("Invalid username or password.");
          return;
        }
        setError(err instanceof ApiClientError ? err.message : "Login failed.");
      }
    });
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div className="space-y-2">
        <label htmlFor="login-username" className="block text-sm font-medium text-aegis-ink">
          Username
        </label>
        <input
          id="login-username"
          name="username"
          type="text"
          autoComplete="username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          disabled={isPending}
          className="w-full rounded border border-aegis-line bg-aegis-surface px-3 py-2 text-aegis-ink outline-none focus:border-aegis-accent"
        />
      </div>

      <div className="space-y-2">
        <label htmlFor="login-password" className="block text-sm font-medium text-aegis-ink">
          Password
        </label>
        <input
          id="login-password"
          name="password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          disabled={isPending}
          className="w-full rounded border border-aegis-line bg-aegis-surface px-3 py-2 text-aegis-ink outline-none focus:border-aegis-accent"
        />
      </div>

      {error ? (
        <p className="text-sm text-aegis-danger" role="alert">
          {error}
        </p>
      ) : null}

      <button
        type="submit"
        disabled={isPending}
        className="w-full rounded bg-aegis-accent px-4 py-2 font-medium text-white transition hover:brightness-110 disabled:opacity-60"
      >
        {isPending ? "Signing in..." : "Sign in"}
      </button>
    </form>
  );
}
