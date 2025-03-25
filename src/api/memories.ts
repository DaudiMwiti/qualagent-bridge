
import { useQuery } from "@tanstack/react-query";

// Define types for memories
export interface Memory {
  id: number;
  text: string;
  memory_type: string;
  timestamp: number;
  metadata: Record<string, any>;
  tag?: string;
}

// API functions
async function fetchMemories(projectId: number, options: { limit?: number; agent_id?: number; memory_type?: string } = {}) {
  const { limit = 5, agent_id, memory_type } = options;
  
  let url = `/api/v1/analysis/memory/recent?project_id=${projectId}&limit=${limit}`;
  
  if (agent_id) {
    url += `&agent_id=${agent_id}`;
  }
  
  if (memory_type) {
    url += `&memory_type=${memory_type}`;
  }
  
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch memories for project ${projectId}`);
  }
  return response.json();
}

// React Query hooks
export function useProjectMemories(
  projectId: number, 
  options: { limit?: number; agent_id?: number; memory_type?: string } = {}
) {
  return useQuery({
    queryKey: ["memories", projectId, options],
    queryFn: () => fetchMemories(projectId, options),
    enabled: !!projectId,
  });
}
