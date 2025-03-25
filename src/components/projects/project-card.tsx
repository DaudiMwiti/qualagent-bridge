
import { Project } from "@/api/projects";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowRight, Calendar } from "lucide-react";
import { useNavigate } from "react-router-dom";

interface ProjectCardProps {
  project: Project;
}

export function ProjectCard({ project }: ProjectCardProps) {
  const navigate = useNavigate();
  const createdDate = new Date(project.created_at).toLocaleDateString();
  
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">{project.name}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground line-clamp-2 mb-4">
          {project.description || "No description provided"}
        </p>
        <div className="flex items-center text-xs text-muted-foreground">
          <Calendar className="h-3 w-3 mr-1" />
          Created on {createdDate}
        </div>
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
  );
}
