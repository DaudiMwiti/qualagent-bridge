
import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { StatusBadge } from "@/components/ui/status-badge";
import { PlusCircle, Calendar, ClipboardList, Brain, MoreVertical } from "lucide-react";
import { useProject } from "@/api/projects";
import { useProjectAnalyses } from "@/api/analysis";
import { useProjectMemories } from "@/api/memories";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export default function ProjectDetail() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const id = projectId ? parseInt(projectId) : 0;
  
  const { data: project, isLoading: isLoadingProject } = useProject(id);
  const { data: analyses, isLoading: isLoadingAnalyses } = useProjectAnalyses(id);
  const { data: memoriesResponse, isLoading: isLoadingMemories } = useProjectMemories(id, { limit: 10 });
  const memories = memoriesResponse?.memories || [];
  
  const [activeTab, setActiveTab] = useState("analyses");
  
  if (isLoadingProject) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-8 bg-muted rounded w-1/4" />
        <div className="h-4 bg-muted rounded w-1/3" />
        <div className="h-[400px] bg-muted rounded" />
      </div>
    );
  }
  
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
        title={project.name} 
        description={project.description || "No description provided"}
        breadcrumbs={[
          { label: "Projects", href: "/projects" },
          { label: project.name, href: `/projects/${project.id}` },
        ]}
        actions={
          <div className="flex space-x-2">
            <Button 
              onClick={() => navigate(`/projects/${project.id}/analysis/new`)}
            >
              <PlusCircle className="mr-2 h-4 w-4" />
              New Analysis
            </Button>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="icon">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem>Edit Project</DropdownMenuItem>
                <DropdownMenuItem className="text-destructive">Delete Project</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        }
      />
      
      <div className="flex items-center text-sm text-muted-foreground mb-6">
        <Calendar className="h-4 w-4 mr-2" />
        Created on {new Date(project.created_at).toLocaleDateString()}
      </div>
      
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-6">
          <TabsTrigger value="analyses">
            <ClipboardList className="h-4 w-4 mr-2" />
            Analyses
          </TabsTrigger>
          <TabsTrigger value="memories">
            <Brain className="h-4 w-4 mr-2" />
            Project Memories
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="analyses">
          {isLoadingAnalyses ? (
            <div className="animate-pulse space-y-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-16 bg-muted rounded" />
              ))}
            </div>
          ) : analyses?.length === 0 ? (
            <div className="text-center p-12 border rounded-md bg-muted/10">
              <h3 className="text-lg font-medium mb-2">No analyses yet</h3>
              <p className="text-muted-foreground mb-6">
                Start your first analysis to gain insights from your research data
              </p>
              <Button onClick={() => navigate(`/projects/${project.id}/analysis/new`)}>
                <PlusCircle className="mr-2 h-4 w-4" />
                Start New Analysis
              </Button>
            </div>
          ) : (
            <div className="rounded-md border overflow-hidden">
              <div className="relative overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-muted text-xs uppercase">
                    <tr>
                      <th className="px-6 py-3 text-left">ID</th>
                      <th className="px-6 py-3 text-left">Status</th>
                      <th className="px-6 py-3 text-left">Created</th>
                      <th className="px-6 py-3 text-left">Completed</th>
                      <th className="px-6 py-3 text-left">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analyses.map((analysis) => (
                      <tr key={analysis.id} className="border-b hover:bg-muted/50">
                        <td className="px-6 py-4 font-medium">#{analysis.id}</td>
                        <td className="px-6 py-4">
                          <StatusBadge status={analysis.status} />
                        </td>
                        <td className="px-6 py-4 text-sm">
                          {new Date(analysis.created_at).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 text-sm">
                          {analysis.completed_at 
                            ? new Date(analysis.completed_at).toLocaleString() 
                            : "-"}
                        </td>
                        <td className="px-6 py-4">
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => navigate(`/projects/${project.id}/analysis/${analysis.id}`)}
                          >
                            View
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </TabsContent>
        
        <TabsContent value="memories">
          {isLoadingMemories ? (
            <div className="animate-pulse space-y-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-24 bg-muted rounded" />
              ))}
            </div>
          ) : memories.length === 0 ? (
            <div className="text-center p-12 border rounded-md bg-muted/10">
              <h3 className="text-lg font-medium mb-2">No memories yet</h3>
              <p className="text-muted-foreground mb-6">
                Memories are created when you run analyses with memory-enabled agents
              </p>
              <Button onClick={() => navigate(`/projects/${project.id}/analysis/new`)}>
                <PlusCircle className="mr-2 h-4 w-4" />
                Start New Analysis
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {memories.map((memory) => (
                <div key={memory.id} className="border rounded-md p-4 bg-card">
                  <div className="flex justify-between mb-2">
                    <div>
                      <span className="inline-block px-2 py-1 text-xs rounded bg-primary/10 text-primary mr-2">
                        {memory.memory_type}
                      </span>
                      {memory.tag && (
                        <span className="inline-block px-2 py-1 text-xs rounded bg-muted">
                          {memory.tag}
                        </span>
                      )}
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {new Date(memory.timestamp * 1000).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-sm">{memory.text}</p>
                </div>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
