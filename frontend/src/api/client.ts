import axios, { AxiosError } from "axios";
import type {
  AnalysisResponse,
  ApiError,
  HealthResponse,
  RunsListResponse,
  SimilarityRequest,
  SimilarityResponse,
  ValidationResponse,
} from "./types";

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  `${window.location.protocol}//${window.location.hostname}:8000/api`;

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export function extractErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const axiosError = err as AxiosError<ApiError>;
    if (axiosError.response?.data?.detail) {
      return typeof axiosError.response.data.detail === "string"
        ? axiosError.response.data.detail
        : JSON.stringify(axiosError.response.data.detail);
    }
    if (axiosError.message) {
      return axiosError.message;
    }
  }
  return "An unexpected error occurred. Ensure the FastAPI backend is running.";
}

export async function uploadAndAnalyze(files: File[]): Promise<AnalysisResponse> {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));
  const response = await apiClient.post<AnalysisResponse>("/analyze", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function fetchAnalysisRun(runId: number): Promise<AnalysisResponse> {
  const response = await apiClient.get<AnalysisResponse>(`/analyze/${runId}`);
  return response.data;
}

export async function fetchRuns(limit = 20, offset = 0): Promise<RunsListResponse> {
  const response = await apiClient.get<RunsListResponse>("/runs", {
    params: { limit, offset },
  });
  return response.data;
}

export async function triggerValidation(): Promise<ValidationResponse> {
  const response = await apiClient.post<ValidationResponse>("/validation/run");
  return response.data;
}

export async function fetchLatestValidation(): Promise<ValidationResponse> {
  const response = await apiClient.get<ValidationResponse>("/validation/latest");
  return response.data;
}

export async function fetchValidationRun(runId: number): Promise<ValidationResponse> {
  const response = await apiClient.get<ValidationResponse>(`/validation/${runId}`);
  return response.data;
}

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await apiClient.get<HealthResponse>("/health");
  return response.data;
}

export async function checkSimilarity(
  request: SimilarityRequest
): Promise<SimilarityResponse> {
  const response = await apiClient.post<SimilarityResponse>(
    "/similarity",
    request
  );
  return response.data;
}
