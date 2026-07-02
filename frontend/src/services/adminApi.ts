"""Admin API helpers with optional X-Admin-Key header."""
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const STORAGE_KEY = "lawyer_admin_api_key";

export function getStoredAdminKey(): string {
  if (typeof window === "undefined") return "";
  return window.sessionStorage.getItem(STORAGE_KEY) || "";
}

export function storeAdminKey(value: string): void {
  if (typeof window === "undefined") return;
  window.sessionStorage.setItem(STORAGE_KEY, value.trim());
}

export function adminHeaders(): HeadersInit {
  const key = getStoredAdminKey();
  return key ? { "X-Admin-Key": key } : {};
}

export async function fetchAdmin(path: string): Promise<Response> {
  return fetch(`${API_URL}/api/v1/admin${path}`, { headers: adminHeaders() });
}
