import { useAuth } from "@clerk/nextjs";

const BASE = process.env.NEXT_PUBLIC_API_URL || "https://saas-application-saas.up.railway.app";

export function useApi() {
  const { getToken, isSignedIn, isLoaded } = useAuth();

  async function req<T>(endpoint: string, opts: RequestInit = {}): Promise<T> {
    // Wait for Clerk to load
    if (!isLoaded) {
      console.warn("Auth not loaded yet, waiting...");
      throw new Error("Authentication not ready. Please wait.");
    }
    
    // Check if user is signed in
    if (!isSignedIn) {
      console.warn("User not signed in");
      throw new Error("You must be signed in to make API requests");
    }

    // Get the token
    const token = await getToken({ template: "default" });
    
    if (!token) {
      console.error("No token available - token is null");
      throw new Error("No authentication token available. Please sign out and sign in again.");
    }

    console.log("API Request:", endpoint, "Token exists:", !!token);

    const res = await fetch(`${BASE}${endpoint}`, {
      ...opts,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
        ...opts.headers,
      },
    });
    
    if (!res.ok) {
      const errorText = await res.text();
      let errorDetail = `HTTP ${res.status}`;
      try {
        const errorJson = JSON.parse(errorText);
        errorDetail = errorJson.detail || errorDetail;
      } catch {
        errorDetail = errorText || errorDetail;
      }
      console.error("API Error:", endpoint, res.status, errorDetail);
      throw new Error(errorDetail);
    }
    
    return res.json();
  }

  return {
    get: <T>(endpoint: string) => req<T>(endpoint),
    post: <T>(endpoint: string, body: unknown) =>
      req<T>(endpoint, { method: "POST", body: JSON.stringify(body) }),
    put: <T>(endpoint: string, body: unknown) =>
      req<T>(endpoint, { method: "PUT", body: JSON.stringify(body) }),
    patch: <T>(endpoint: string, body: unknown) =>
      req<T>(endpoint, { method: "PATCH", body: JSON.stringify(body) }),
    delete: <T>(endpoint: string) =>
      req<T>(endpoint, { method: "DELETE" }),
  };
}