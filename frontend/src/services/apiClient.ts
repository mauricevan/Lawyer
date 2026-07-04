/** Central API base URL for all frontend services. */
const DEFAULT_API_URL = "http://localhost:8001";

export function getApiUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL || DEFAULT_API_URL;
}

export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${getApiUrl()}/health`, { cache: "no-store" });
    if (!response.ok) return false;
    const data = (await response.json()) as { status?: string };
    return data.status === "ok";
  } catch {
    return false;
  }
}
