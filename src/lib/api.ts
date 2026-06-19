/**
 * API base URL resolver.
 *
 * In production (automindai.info): nginx proxies /api/ → backend:8000/api/
 *   so we use relative "/api" — cookies work because same domain.
 *
 * In development (localhost): vite proxy handles /api → http://localhost:8000/api
 *   so we also use relative "/api".
 *
 * The VITE_API_URL env var is an escape hatch for non-standard deployments.
 */
export const API_URL: string = import.meta.env.VITE_API_URL || "/api";

/**
 * Standard fetch wrapper that always includes credentials (cookies).
 */
export async function apiFetch(
  path: string,
  options: RequestInit = {}
): Promise<Response> {
  const url = `${API_URL}${path}`;
  return fetch(url, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });
}
