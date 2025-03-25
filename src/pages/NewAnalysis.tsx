
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function NewAnalysis() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const projectIdNum = projectId ? parseInt(projectId) : 0;
  const { data: project } = useProject(projectIdNum);
  const { data: agents, isLoading: isLoadingAgents } = useAgents();
  
  const [agentId, setAgentId] = useState<string>("");
  const [researchText, setResearchText] = useState("");
  const [objective, setObjective] = useState("Identify key themes and insights");
  
  const { mutate: createAnalysis, isPending } = useCreateAnalysis();
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!agentId) {
      toast({
        title: "Agent selection required",
        description: "Please select an agent to perform the analysis",
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
      agent_id: parseInt(agentId),
      data: {
        text_data: researchText,
        parameters: {
          research_objective: objective,
          include_quotes: true
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
          <Label htmlFor="agent">Select Agent</Label>
          <Select
            value={agentId}
            onValueChange={setAgentId}
          >
            <SelectTrigger id="agent" className="w-full">
              <SelectValue placeholder="Select an agent" />
            </SelectTrigger>
            <SelectContent>
              {isLoadingAgents ? (
                <SelectItem value="loading" disabled>
                  Loading agents...
                </SelectItem>
              ) : agents?.length === 0 ? (
                <SelectItem value="none" disabled>
                  No agents available
                </SelectItem>
              ) : (
                agents?.map((agent) => (
                  <SelectItem key={agent.id} value={agent.id.toString()}>
                    {agent.name}
                  </SelectItem>
                ))
              )}
            </SelectContent>
          </Select>
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
          <Button type="submit" disabled={isPending}>
            {isPending ? "Starting Analysis..." : "Start Analysis"}
          </Button>
        </div>
      </form>
    </div>
  );
}
