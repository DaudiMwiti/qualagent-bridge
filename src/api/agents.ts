
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

// Define types for agents
export interface Agent {
  id: number;
  name: string;
  description?: string;
  model: string;
  configuration: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface AgentCreate {
  name: string;
  description?: string;
  model: string;
  configuration: Record<string, any>;
}

// API functions
async function fetchAgents() {
  const response = await fetch("/api/v1/agents");
  if (!response.ok) {
    throw new Error("Failed to fetch agents");
  }
  return response.json();
}

async function fetchAgent(id: number) {
  const response = await fetch(`/api/v1/agents/${id}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch agent ${id}`);
  }
  return response.json();
}

async function createAgent(data: AgentCreate) {
  const response = await fetch("/api/v1/agents", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    throw new Error("Failed to create agent");
  }
  
  return response.json();
}

// React Query hooks
export function useAgents() {
  return useQuery({
    queryKey: ["agents"],
    queryFn: fetchAgents,
  });
}

export function useAgent(id: number) {
  return useQuery({
    queryKey: ["agent", id],
    queryFn: () => fetchAgent(id),
    enabled: !!id,
  });
}

export function useCreateAgent() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: createAgent,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agents"] });
    },
  });
}
