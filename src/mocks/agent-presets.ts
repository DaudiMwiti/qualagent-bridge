
import { AgentPreset } from "@/types/agent-presets";

// Mock data for agent presets
export const mockAgentPresets: AgentPreset[] = [
  {
    id: "1",
    name: "Thematic Analyst",
    description: "Specializes in identifying recurring themes and patterns across qualitative data.",
    model: "gpt-4o",
    temperature: 0.2,
    tools: ["theme_cluster", "document_search", "sentiment_analysis"],
    suitableFor: "Interviews, focus groups, open-ended survey responses",
    complexity: "basic"
  },
  {
    id: "2",
    name: "Grounded Theorist",
    description: "Uses inductive reasoning to develop theories from data without preconceptions.",
    model: "gpt-4o",
    temperature: 0.4,
    tools: ["generate_insight", "document_search", "summarize_memory"],
    suitableFor: "Exploratory research, theory development, novel domains",
    complexity: "intermediate"
  },
  {
    id: "3",
    name: "Narrative Researcher",
    description: "Analyzes storytelling patterns and personal experiences in qualitative data.",
    model: "gpt-4o",
    temperature: 0.7,
    tools: ["document_search", "sentiment_analysis", "retrieve_memories"],
    suitableFor: "Life histories, personal accounts, ethnographic research",
    complexity: "intermediate"
  },
  {
    id: "4",
    name: "Discourse Analyst",
    description: "Examines communication patterns, power dynamics, and social contexts.",
    model: "gpt-4o",
    temperature: 0.5,
    tools: ["document_search", "sentiment_analysis", "theme_cluster", "summarize_memories"],
    suitableFor: "Media analysis, political texts, conversation analysis",
    complexity: "advanced"
  },
  {
    id: "5",
    name: "Phenomenologist",
    description: "Focuses on lived experiences and how individuals perceive events.",
    model: "gpt-4o",
    temperature: 0.6,
    tools: ["generate_insight", "document_search", "retrieve_memories"],
    suitableFor: "Experience-centered research, perception studies",
    complexity: "advanced"
  }
];

// Function to simulate fetching presets from an API
export function fetchMockAgentPresets(): Promise<AgentPreset[]> {
  return new Promise((resolve) => {
    // Simulate network delay
    setTimeout(() => {
      resolve(mockAgentPresets);
    }, 800);
  });
}
