
import { useState, useEffect } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { useAgents } from "@/api/agents";
import { useAgentPresets } from "@/api/agent-presets";
import { AgentPresetSelector } from "@/components/agents/agent-preset-selector";
import { AgentPreset } from "@/types/agent-presets";
import { fetchMockAgentPresets } from "@/mocks/agent-presets";

export default function Agents() {
  const { toast } = useToast();
  const { data: agents, isLoading: isLoadingAgents } = useAgents();
  const { data: presets, isLoading: isLoadingPresets } = useAgentPresets();
  
  // For development/demo purposes, load mock data if API fails
  const [mockPresets, setMockPresets] = useState<AgentPreset[]>([]);
  const [selectedPreset, setSelectedPreset] = useState<AgentPreset | null>(null);
  
  useEffect(() => {
    // If the real API fails to load presets, use mock data
    if (!isLoadingPresets && !presets) {
      fetchMockAgentPresets().then(setMockPresets);
    }
  }, [isLoadingPresets, presets]);
  
  // Use API presets if available, otherwise fall back to mock data
  const displayPresets = presets || mockPresets;
  
  const handlePresetSelect = (preset: AgentPreset) => {
    setSelectedPreset(preset);
    toast({
      title: "Agent Selected",
      description: `You selected the ${preset.name} agent preset`,
    });
  };
  
  return (
    <div>
      <PageHeader
        title="AI Agents"
        description="Configure and manage your AI research agents"
      />
      
      <Tabs defaultValue="presets" className="mt-6">
        <TabsList>
          <TabsTrigger value="presets">Agent Presets</TabsTrigger>
          <TabsTrigger value="custom">Custom Agents</TabsTrigger>
        </TabsList>
        
        <TabsContent value="presets" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Agent Presets</CardTitle>
              <CardDescription>
                Choose from these pre-configured AI agents optimized for different types of qualitative analysis.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <AgentPresetSelector
                presets={displayPresets}
                selectedPresetId={selectedPreset?.id || null}
                onSelectPreset={handlePresetSelect}
                isLoading={isLoadingPresets && mockPresets.length === 0}
              />
              
              {selectedPreset && (
                <div className="mt-6">
                  <h3 className="text-lg font-medium mb-2">Agent Configuration</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Model</p>
                      <p>{selectedPreset.model}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Temperature</p>
                      <p>{selectedPreset.temperature}</p>
                    </div>
                    <div className="md:col-span-2">
                      <p className="text-sm font-medium text-muted-foreground">Available Tools</p>
                      <p>{selectedPreset.tools.join(", ")}</p>
                    </div>
                  </div>
                  
                  <div className="flex justify-end mt-4">
                    <Button>Use This Agent</Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="custom" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Custom Agents</CardTitle>
              <CardDescription>
                View and manage your custom AI agents.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoadingAgents ? (
                <p>Loading custom agents...</p>
              ) : agents?.length ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {agents.map((agent) => (
                    <Card key={agent.id}>
                      <CardHeader>
                        <CardTitle>{agent.name}</CardTitle>
                        <CardDescription>{agent.description || "No description available"}</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <p><strong>Model:</strong> {agent.model}</p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <p>No custom agents created yet.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
