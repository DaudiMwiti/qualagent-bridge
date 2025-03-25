
export interface AgentPreset {
  id: string;
  name: string;
  description: string;
  model: string;
  temperature: number;
  tools: string[];
  suitableFor?: string;
  complexity?: 'basic' | 'intermediate' | 'advanced';
}
