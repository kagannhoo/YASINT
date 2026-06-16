import type {
  Analysis,
  AnalysisListItem,
  DashboardStats,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      ...(options?.headers || {}),
    },
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

export async function getDashboardStats(): Promise<DashboardStats> {
  return request<DashboardStats>("/api/analysis/stats");
}

export async function getAnalysisHistory(
  limit = 50,
  offset = 0
): Promise<AnalysisListItem[]> {
  return request<AnalysisListItem[]>(
    `/api/analysis/history?limit=${limit}&offset=${offset}`
  );
}

export async function getAnalysis(id: string): Promise<Analysis> {
  return request<Analysis>(`/api/analysis/${id}`);
}

export async function startAnalysis(formData: FormData): Promise<{
  analysis_id: string;
  status: string;
}> {
  const res = await fetch(`${API_URL}/api/analysis/start`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

export function getPdfUrl(analysisId: string): string {
  return `${API_URL}/api/analysis/${analysisId}/report/pdf`;
}

export function getJsonExportUrl(analysisId: string): string {
  return `${API_URL}/api/analysis/${analysisId}/export/json`;
}

export function getWsUrl(analysisId: string): string {
  const wsBase =
    process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";
  return `${wsBase}/ws/${analysisId}`;
}
