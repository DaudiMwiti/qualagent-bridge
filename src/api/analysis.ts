
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

// Define types for analyses
export interface Analysis {
  id: number;
  project_id: number;
  agent_id: number;
  data: Record<string, any>;
  status: "pending" | "in_progress" | "completed" | "failed";
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export interface AnalysisCreate {
  project_id: number;
  agent_id: number;
  data: Record<string, any>;
}

export interface Memory {
  id: string;
  text: string;
  memory_type: string;
  tag?: string;
  score?: number;
  timestamp?: number;
  metadata?: Record<string, any>;
}

export interface QuoteSource {
  document_id?: string;
  chunk_id?: number;
  start_char?: number;
  end_char?: number;
  metadata?: {
    filename?: string;
    paragraph?: number;
    [key: string]: any;
  };
}

export interface Quote {
  text: string;
  source?: QuoteSource;
}

export interface Theme {
  name: string;
  description: string;
  keywords?: string[];
  quotes?: (string | Quote)[];
}

export interface AnalysisResults {
  themes?: Theme[];
  insights?: Array<string | {
    theme: string;
    quote?: string;
    summary?: string;
    source?: QuoteSource;
  }>;
  summary?: string;
  sentiment?: {
    overall: string;
    score: number;
    breakdown?: Record<string, any>;
  };
  memory_used?: Memory[];
  [key: string]: any;
}

// API functions
async function fetchAnalyses(projectId: number) {
  const response = await fetch(`/api/v1/analysis/project/${projectId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch analyses for project ${projectId}`);
  }
  return response.json();
}

async function fetchAnalysis(id: number) {
  const response = await fetch(`/api/v1/analysis/${id}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch analysis ${id}`);
  }
  return response.json();
}

async function fetchAnalysisResults(id: number) {
  const response = await fetch(`/api/v1/analysis/${id}/results`);
  if (!response.ok) {
    throw new Error(`Failed to fetch results for analysis ${id}`);
  }
  return response.json();
}

async function createAnalysis(data: AnalysisCreate) {
  const response = await fetch("/api/v1/analysis", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    throw new Error("Failed to create analysis");
  }
  
  return response.json();
}

// React Query hooks
export function useProjectAnalyses(projectId: number) {
  return useQuery({
    queryKey: ["analyses", projectId],
    queryFn: () => fetchAnalyses(projectId),
    enabled: !!projectId,
  });
}

export function useAnalysis(id: number) {
  return useQuery({
    queryKey: ["analysis", id],
    queryFn: () => fetchAnalysis(id),
    enabled: !!id,
  });
}

export function useAnalysisResults(id: number, status: string) {
  return useQuery({
    queryKey: ["analysis-results", id],
    queryFn: () => fetchAnalysisResults(id),
    enabled: !!id && status === "completed",
  });
}

export function useCreateAnalysis() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: createAnalysis,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["analyses", data.project_id] });
    },
  });
}
