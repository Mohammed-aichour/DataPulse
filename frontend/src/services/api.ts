import {
  CoursePerformance,
  FactorPerformance,
  GradeDistributionBin,
  HealthInfo,
  ModelEvaluation,
  OverviewKPIs,
  PaginatedStudents,
  PipelineHistoryItem,
  PipelineStatus,
  PredictionRequest,
  PredictionResponse,
  StudentDetail,
} from "../types";

export const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  (import.meta.env.DEV ? "http://localhost:8000/api" : "/api");

async function fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP Error ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

export const api = {
  // System
  getHealth: () => fetchJson<HealthInfo>("/health"),
  getInfo: () => fetchJson<any>("/info"),

  // Analytics
  getOverviewKPIs: () => fetchJson<OverviewKPIs>("/analytics/overview"),
  getCourses: () => fetchJson<CoursePerformance[]>("/analytics/courses"),
  getGradeDistribution: () => fetchJson<GradeDistributionBin[]>("/analytics/distribution"),
  getPerformanceByFactor: (factor: string) => fetchJson<FactorPerformance[]>(`/analytics/performance?factor=${factor}`),
  getCorrelations: () => fetchJson<any[]>("/analytics/correlations"),
  getDataQuality: () => fetchJson<any>("/analytics/data-quality"),

  // Students
  getStudents: (params: {
    page?: number;
    page_size?: number;
    search?: string;
    school?: string;
    course?: string;
    risk_only?: boolean;
  }) => {
    const query = new URLSearchParams();
    if (params.page) query.set("page", params.page.toString());
    if (params.page_size) query.set("page_size", params.page_size.toString());
    if (params.search) query.set("search", params.search);
    if (params.school) query.set("school", params.school);
    if (params.course) query.set("course", params.course);
    if (params.risk_only) query.set("risk_only", "true");
    return fetchJson<PaginatedStudents>(`/students?${query.toString()}`);
  },
  getStudentDetail: (studentId: string) => fetchJson<StudentDetail>(`/students/${studentId}`),

  // Machine Learning
  getModelEvaluation: () => fetchJson<ModelEvaluation>("/ml/evaluation"),
  predict: (data: PredictionRequest) =>
    fetchJson<PredictionResponse>("/ml/predict", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Pipeline
  getPipelineStatus: () => fetchJson<PipelineStatus>("/pipeline/status"),
  getPipelineHistory: () => fetchJson<PipelineHistoryItem[]>("/pipeline/history"),
  runPipeline: () =>
    fetchJson<{
      status: string;
      duration_seconds: number;
      records_processed: number;
      quality_score: number;
      details: any;
    }>("/pipeline/run", {
      method: "POST",
    }),

  // Export
  getCsvExportUrl: (dataset: string) => `${API_BASE_URL}/export/csv/${dataset}`,
  getPowerBiSpec: () => fetchJson<any>("/export/powerbi-spec"),
};
