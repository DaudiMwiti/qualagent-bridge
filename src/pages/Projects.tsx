
import { useNavigate } from "react-router-dom";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ProjectCard } from "@/components/projects/project-card";
import { PlusCircle, Search } from "lucide-react";
import { useProjects } from "@/api/projects";
import { useState } from "react";

export default function Projects() {
  const navigate = useNavigate();
  const { data: projects, isLoading } = useProjects();
  const [searchQuery, setSearchQuery] = useState("");
  
  const filteredProjects = projects?.filter(project => 
    project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (project.description && project.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );
  
  return (
    <div>
      <PageHeader 
        title="Projects" 
        description="View and manage your research projects"
        actions={
          <Button onClick={() => navigate("/projects/new")}>
            <PlusCircle className="mr-2 h-4 w-4" />
            New Project
          </Button>
        }
      />
      
      <div className="flex items-center mb-6">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search projects..."
            className="pl-8"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>
      
      {isLoading ? (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="animate-pulse rounded-md border h-[200px] bg-muted/20" />
          ))}
        </div>
      ) : (
        <>
          {filteredProjects?.length === 0 ? (
            <div className="text-center p-12 border rounded-md bg-muted/10">
              <h3 className="text-lg font-medium mb-2">No projects found</h3>
              <p className="text-muted-foreground mb-6">
                {searchQuery 
                  ? "No projects match your search criteria" 
                  : "You haven't created any projects yet"}
              </p>
              <Button onClick={() => navigate("/projects/new")}>
                <PlusCircle className="mr-2 h-4 w-4" />
                Create Your First Project
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
              {filteredProjects?.map((project) => (
                <ProjectCard key={project.id} project={project} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
