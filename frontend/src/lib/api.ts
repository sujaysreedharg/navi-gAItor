import axios from 'axios';
import type { AiAgentRequest, AiAgentResponse, AnalysisResponse } from '../types';

const baseURL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export async function analyzeFlight(file: File, onUploadProgress?: (progress: number) => void) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post<AnalysisResponse>('/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (event) => {
      if (!event.total) return;
      const percent = Math.round((event.loaded / event.total) * 100);
      onUploadProgress?.(percent);
    },
  });

  return response.data;
}

export async function runAiAgent(request: AiAgentRequest) {
  const response = await apiClient.post<AiAgentResponse>('/ai/agent', request);
  return response.data;
}
