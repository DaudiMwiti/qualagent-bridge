
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { useCreateProject } from "@/api/projects";

export default function NewProject() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  
  const { mutate: createProject, isPending } = useCreateProject();
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name.trim()) {
      toast({
        title: "Project name required",
        description: "Please enter a name for your project",
        variant: "destructive",
      });
      return;
    }
    
    createProject(
      { name, description },
      {
        onSuccess: (data) => {
          toast({
            title: "Project created",
            description: "Your new project has been created successfully",
          });
          navigate(`/dashboard/projects/${data.id}`);
        },
        onError: (error) => {
          toast({
            title: "Error",
            description: error instanceof Error ? error.message : "Failed to create project",
            variant: "destructive",
          });
        },
      }
    );
  };
  
  return (
    <div>
      <PageHeader 
        title="Create New Project" 
        description="Set up a new qualitative research project"
        breadcrumbs={[
          { label: "Projects", href: "/dashboard/projects" },
          { label: "New Project", href: "/dashboard/projects/new" },
        ]}
      />
      
      <div className="max-w-xl">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="name">Project Name</Label>
            <Input
              id="name"
              placeholder="E.g., Customer Feedback Analysis"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              placeholder="What is the purpose of this research project?"
              rows={5}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          
          <div className="flex justify-end space-x-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate("/dashboard/projects")}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isPending}>
              {isPending ? "Creating..." : "Create Project"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
