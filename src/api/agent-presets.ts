
import { useQuery } from "@tanstack/react-query";
import { AgentPreset } from "@/types/agent-presets";

// API function to fetch agent presets
async function fetchAgentPresets() {
  const response = await fetch("/api/v1/agents/presets");
  if (!response.ok) {
    throw new Error("Failed to fetch agent presets");
  }
  return response.json() as Promise<AgentPreset[]>;
}

// React Query hook
export function useAgentPresets() {
  return useQuery({
    queryKey: ["agent-presets"],
    queryFn: fetchAgentPresets,
  });
}
