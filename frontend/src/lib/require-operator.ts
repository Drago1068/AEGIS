/**
 * Server-side operator session gate for console pages.
 *
 * The session cookie is issued by the API origin; Next.js SSR must forward it
 * when calling the backend. Browser calls rely on credentials: "include".
 */

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { ApiClientError, getApiBaseUrl, getMe } from "./api-client";

export const SESSION_COOKIE_NAME = "aegis_session";

export async function getForwardedSessionCookie(): Promise<string | undefined> {
  const store = await cookies();
  const session = store.get(SESSION_COOKIE_NAME);
  if (!session?.value) {
    return undefined;
  }
  return `${SESSION_COOKIE_NAME}=${session.value}`;
}

export async function requireOperator(): Promise<{ username: string; cookie?: string }> {
  const cookie = await getForwardedSessionCookie();
  try {
    const me = await getMe(getApiBaseUrl(), { cookie, skipAuthRedirect: true });
    return { username: me.username, cookie };
  } catch (err) {
    if (err instanceof ApiClientError && err.status === 401) {
      redirect("/login");
    }
    redirect("/login");
  }
}
