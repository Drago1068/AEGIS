"use client";

import { useRouter } from "next/navigation";
import { useTransition } from "react";

import { getApiBaseUrl, logout } from "@/lib/api-client";

type OperatorSessionBarProps = {
  username: string;
};

export function OperatorSessionBar({ username }: OperatorSessionBarProps) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const baseUrl = getApiBaseUrl();

  function onLogout() {
    startTransition(async () => {
      try {
        await logout(baseUrl);
      } catch {
        // Cookie clear may fail if the session already expired; still leave the console.
      }
      router.replace("/login");
      router.refresh();
    });
  }

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 text-sm text-aegis-muted">
      <p>
        Signed in as <span className="font-medium text-aegis-ink">{username}</span>
      </p>
      <button
        type="button"
        onClick={onLogout}
        disabled={isPending}
        className="rounded border border-aegis-line px-3 py-1 text-aegis-muted transition hover:border-aegis-danger hover:text-aegis-danger disabled:opacity-60"
      >
        {isPending ? "Signing out..." : "Sign out"}
      </button>
    </div>
  );
}
