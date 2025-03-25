
import { useNavigate } from "react-router-dom";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/status-badge";
import { PlusCircle, ArrowRight } from "lucide-react";
import { useProjects } from "@/api/projects";
import { useEffect, useState } from "react";
import { Analysis } from "@/api/analysis";

export default function Dashboard() {
  const navigate = useNavigate();
  const { data: projects, isLoading: isLoadingProjects } = useProjects();
  const [recentAnalyses, setRecentAnalyses] = useState<Analysis[]>([]);
  const [isLoadingAnalyses, setIsLoadingAnalyses] = useState(true);
  
  useEffect(() => {
    // Fetch recent analyses across all projects
    async function fetchRecentAnalyses() {
      try {
        setIsLoadingAnalyses(true);
        // Add a check to prevent API calls in development if the backend is not available
        if (import.meta.env.DEV) {
          // In development, set empty analyses after a delay to simulate loading
          setTimeout(() => {
            setRecentAnalyses([]);
            setIsLoadingAnalyses(false);
          }, 1000);
          return;
        }
        
        const response = await fetch("/api/v1/analysis?limit=5");
        if (response.ok) {
          const data = await response.json();
          setRecentAnalyses(data);
        }
      } catch (error) {
        console.error("Failed to fetch recent analyses:", error);
      } finally {
        setIsLoadingAnalyses(false);
      }
    }
    
    fetchRecentAnalyses();
  }, []);
  
  return (
    <div>
      <PageHeader 
        title="Dashboard" 
        description="Overview of your qualitative research projects"
        actions={
          <Button onClick={() => navigate("/dashboard/projects/new")}>
            <PlusCircle className="mr-2 h-4 w-4" />
            New Project
          </Button>
        }
      />
      
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 mb-8">
        {isLoadingProjects ? (
          Array.from({ length: 3 }).map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader className="bg-muted h-20" />
              <CardContent className="h-24" />
            </Card>
          ))
        ) : (
          <>
            {projects?.slice(0, 6).map((project) => (
              <Card key={project.id} className="overflow-hidden">
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg">{project.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {project.description || "No description provided"}
                  </p>
                </CardContent>
                <CardFooter className="border-t p-4 bg-muted/20">
                  <Button 
                    variant="ghost" 
                    className="ml-auto" 
                    size="sm"
                    onClick={() => navigate(`/dashboard/projects/${project.id}`)}
                  >
                    View Details
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </CardFooter>
              </Card>
            ))}
            
            <Card className="border-dashed flex items-center justify-center">
              <CardContent className="flex flex-col items-center justify-center p-6 text-center">
                <PlusCircle className="h-12 w-12 text-muted-foreground mb-2" />
                <h3 className="text-lg font-medium">Create New Project</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Start a new research initiative
                </p>
                <Button onClick={() => navigate("/dashboard/projects/new")}>New Project</Button>
              </CardContent>
            </Card>
          </>
        )}
      </div>
      
      <h2 className="text-xl font-semibold mb-4">Recent Analyses</h2>
      <div className="rounded-md border overflow-hidden">
        {isLoadingAnalyses ? (
          <div className="animate-pulse p-6">
            <div className="h-4 bg-muted rounded w-1/3 mb-6" />
            <div className="space-y-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-12 bg-muted rounded" />
              ))}
            </div>
          </div>
        ) : (
          <div className="relative overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted text-xs uppercase">
                <tr>
                  <th className="px-6 py-3 text-left">ID</th>
                  <th className="px-6 py-3 text-left">Project</th>
                  <th className="px-6 py-3 text-left">Status</th>
                  <th className="px-6 py-3 text-left">Created</th>
                  <th className="px-6 py-3 text-left">Actions</th>
                </tr>
              </thead>
              <tbody>
                {recentAnalyses.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-8 text-center text-muted-foreground">
                      No analyses found. Start your first analysis by creating a project.
                    </td>
                  </tr>
                ) : (
                  recentAnalyses.map((analysis) => (
                    <tr key={analysis.id} className="border-b hover:bg-muted/50">
                      <td className="px-6 py-4 font-medium">#{analysis.id}</td>
                      <td className="px-6 py-4">{analysis.project_id}</td>
                      <td className="px-6 py-4">
                        <StatusBadge status={analysis.status} />
                      </td>
                      <td className="px-6 py-4 text-sm">
                        {new Date(analysis.created_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4">
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => navigate(`/dashboard/projects/${analysis.project_id}/analysis/${analysis.id}`)}
                        >
                          View
                        </Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
        
        <div className="flex justify-center p-4 bg-muted/20">
          <Button
            variant="ghost"
            onClick={() => navigate("/dashboard/projects")}
          >
            View All Projects
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
