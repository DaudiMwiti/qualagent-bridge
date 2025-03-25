
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { useProject } from "@/api/projects";
import { useAgents } from "@/api/agents";
import { useCreateAnalysis } from "@/api/analysis";
import { AgentPresetSelector } from "@/components/agents/agent-preset-selector";
import { useAgentPresets } from "@/api/agent-presets";
import { AgentPreset } from "@/types/agent-presets";
import { AlertCircle } from "lucide-react";
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from "@/components/ui/alert";

export default function NewAnalysis() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const projectIdNum = projectId ? parseInt(projectId) : 0;
  const { data: project } = useProject(projectIdNum);
  
  // Agent presets integration
  const { data: presets, isLoading: isLoadingPresets, isError: isPresetsError } = useAgentPresets();
  const [selectedPreset, setSelectedPreset] = useState<AgentPreset | null>(null);
  
  const [researchText, setResearchText] = useState("");
  const [objective, setObjective] = useState("Identify key themes and insights");
  
  const { mutate: createAnalysis, isPending } = useCreateAnalysis();
  
  const handlePresetSelect = (preset: AgentPreset) => {
    setSelectedPreset(preset);
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedPreset) {
      toast({
        title: "Agent selection required",
        description: "Please select an agent preset to perform the analysis",
        variant: "destructive",
      });
      return;
    }
    
    if (!researchText.trim()) {
      toast({
        title: "Research data required",
        description: "Please enter or paste your research data",
        variant: "destructive",
      });
      return;
    }
    
    const analysisData = {
      project_id: projectIdNum,
      agent_id: parseInt(selectedPreset.id),
      data: {
        text_data: researchText,
        parameters: {
          research_objective: objective,
          include_quotes: true,
          model: selectedPreset.model,
          temperature: selectedPreset.temperature,
          tools: selectedPreset.tools
        }
      }
    };
    
    createAnalysis(analysisData, {
      onSuccess: (data) => {
        toast({
          title: "Analysis started",
          description: "Your analysis has been submitted and is now processing",
        });
        navigate(`/projects/${projectIdNum}/analysis/${data.id}`);
      },
      onError: (error) => {
        toast({
          title: "Error",
          description: error instanceof Error ? error.message : "Failed to start analysis",
          variant: "destructive",
        });
      },
    });
  };
  
  if (!project) {
    return (
      <div className="text-center p-12">
        <h2 className="text-xl font-semibold mb-2">Project not found</h2>
        <p className="text-muted-foreground mb-4">The project you're looking for doesn't exist or has been deleted.</p>
        <Button onClick={() => navigate("/projects")}>Back to Projects</Button>
      </div>
    );
  }
  
  return (
    <div>
      <PageHeader 
        title="New Analysis" 
        description="Analyze your research data with AI agents"
        breadcrumbs={[
          { label: "Projects", href: "/projects" },
          { label: project.name, href: `/projects/${project.id}` },
          { label: "New Analysis", href: `/projects/${project.id}/analysis/new` },
        ]}
      />
      
      <form onSubmit={handleSubmit} className="space-y-6 max-w-3xl">
        <div className="space-y-2">
          <Label htmlFor="agentPreset">Select Analysis Agent</Label>
          
          {isPresetsError && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>
                Failed to load agent presets. Please refresh the page or try again later.
              </AlertDescription>
            </Alert>
          )}
          
          <AgentPresetSelector
            presets={presets || []}
            selectedPresetId={selectedPreset?.id || null}
            onSelectPreset={handlePresetSelect}
            isLoading={isLoadingPresets}
          />
          
          {selectedPreset && (
            <div className="mt-4 p-4 bg-primary/5 border border-primary/20 rounded-lg">
              <h3 className="font-medium">Selected: {selectedPreset.name}</h3>
              <p className="text-sm text-muted-foreground">{selectedPreset.description}</p>
            </div>
          )}
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="objective">Research Objective</Label>
          <Input
            id="objective"
            placeholder="E.g., Identify key themes and insights"
            value={objective}
            onChange={(e) => setObjective(e.target.value)}
          />
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="researchText">Research Data</Label>
          <Textarea
            id="researchText"
            placeholder="Paste your interview transcripts, survey responses, or other research data here..."
            rows={12}
            value={researchText}
            onChange={(e) => setResearchText(e.target.value)}
            className="font-mono text-sm"
          />
        </div>
        
        <div className="flex justify-end space-x-4">
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate(`/projects/${project.id}`)}
          >
            Cancel
          </Button>
          <Button type="submit" disabled={isPending || !selectedPreset}>
            {isPending ? "Starting Analysis..." : "Start Analysis"}
          </Button>
        </div>
      </form>
    </div>
  );
}
