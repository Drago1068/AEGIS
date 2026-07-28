import { LoginForm } from "@/components/LoginForm";
import { getApiBaseUrl, getMe } from "@/lib/api-client";
import { getForwardedSessionCookie } from "@/lib/require-operator";
import { redirect } from "next/navigation";

export const dynamic = "force-dynamic";

export default async function LoginPage() {
  const cookie = await getForwardedSessionCookie();
  if (cookie) {
    try {
      await getMe(getApiBaseUrl(), { cookie, skipAuthRedirect: true });
      redirect("/");
    } catch {
      // Session cookie present but invalid; show the login form.
    }
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-md flex-col justify-center gap-8 px-6 py-10">
      <header className="space-y-2">
        <p className="text-sm font-medium uppercase tracking-[0.18em] text-aegis-accent">
          Decision support
        </p>
        <h1 className="text-4xl font-semibold tracking-tight text-aegis-ink">AEGIS</h1>
        <p className="text-base text-aegis-muted">Sign in to open the operator console.</p>
      </header>

      <section className="rounded-lg border border-aegis-line bg-aegis-panel p-5 shadow-sm">
        <LoginForm />
      </section>
    </main>
  );
}
