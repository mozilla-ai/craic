import type {
  ReviewQueueResponse,
  ReviewDecisionResponse,
  ReviewStatsResponse,
} from "./types";

const API_BASE = "/api";

let token: string | null = null;

export function setToken(t: string | null) {
  token = t;
}

export function getToken(): string | null {
  return token;
}

class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

let onUnauthorized: (() => void) | null = null;

export function setOnUnauthorized(callback: () => void) {
  onUnauthorized = callback;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const resp = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!resp.ok) {
    if (resp.status === 401 && onUnauthorized) {
      onUnauthorized();
    }
    const body = await resp.json().catch(() => ({}));
    throw new ApiError(resp.status, body.detail || `HTTP ${resp.status}`);
  }
  return resp.json();
}

export const api = {
  login: (username: string, password: string) =>
    request<{ token: string; username: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),

  reviewQueue: (limit = 20, offset = 0) =>
    request<ReviewQueueResponse>(
      `/review/queue?limit=${limit}&offset=${offset}`,
    ),

  approve: (unitId: string) =>
    request<ReviewDecisionResponse>(`/review/${unitId}/approve`, {
      method: "POST",
    }),

  reject: (unitId: string) =>
    request<ReviewDecisionResponse>(`/review/${unitId}/reject`, {
      method: "POST",
    }),

  reviewStats: () => request<ReviewStatsResponse>("/review/stats"),
};

export { ApiError };
