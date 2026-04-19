import { useAuth } from "@clerk/nextjs";

const BASE = process.env.NEXT_PUBLIC_API_URL!;

export function useApi() {
  const { getToken } = useAuth();

  async function req<T>(endpoint: string, opts: RequestInit = {}): Promise<T> {
    const token = await getToken();
    const res = await fetch(`${BASE}${endpoint}`, {
      ...opts,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
        ...opts.headers,
      },
    });
    if (!res.ok) {
      const e = await res.json().catch(() => ({}));
      throw new Error(e.detail || `HTTP ${res.status}`);
    }
    return res.json();
  }

  return {
    get: <T>(ep: string) => req<T>(ep),
    post: <T>(ep: string, body: unknown) =>
      req<T>(ep, { method: "POST", body: JSON.stringify(body) }),
    patch: <T>(ep: string, body: unknown) =>
      req<T>(ep, { method: "PATCH", body: JSON.stringify(body) }),
  };
}