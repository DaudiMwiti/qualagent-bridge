
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageHeader } from "@/components/ui/page-header";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { PlusCircle, Search, Settings, User, ArrowRight } from "lucide-react";
import { useAgents } from "@/api/agents";

export default function Agents() {
  const navigate = useNavigate();
  const { data: agents, isLoading } = useAgents();
  const [searchQuery, setSearchQuery] = useState("");
  
  const filteredAgents = agents?.filter(agent => 
    agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (agent.description && agent.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );
  
  return (
    <div>
      <PageHeader 
        title="AI Agents" 
        description="Configure and manage your research agents"
        actions={
          <Button onClick={() => navigate("/agents/new")}>
            <PlusCircle className="mr-2 h-4 w-4" />
            New Agent
          </Button>
        }
      />
      
      <div className="flex items-center mb-6">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search agents..."
            className="pl-8"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>
      
      {isLoading ? (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="animate-pulse rounded-md border h-[200px] bg-muted/20" />
          ))}
        </div>
      ) : (
        <>
          {filteredAgents?.length === 0 ? (
            <div className="text-center p-12 border rounded-md bg-muted/10">
              <h3 className="text-lg font-medium mb-2">No agents found</h3>
              <p className="text-muted-foreground mb-6">
                {searchQuery 
                  ? "No agents match your search criteria" 
                  : "You haven't created any agents yet"}
              </p>
              <Button onClick={() => navigate("/agents/new")}>
                <PlusCircle className="mr-2 h-4 w-4" />
                Create Your First Agent
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
              {filteredAgents?.map((agent) => (
                <Card key={agent.id}>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-lg flex items-center">
                      <User className="h-5 w-5 mr-2 text-primary" />
                      {agent.name}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground line-clamp-2 mb-4">
                      {agent.description || "No description provided"}
                    </p>
                    <div className="flex flex-wrap gap-2">
                      <span className="px-2 py-1 bg-muted rounded-full text-xs">
                        {agent.model}
                      </span>
                      {agent.configuration?.agent_type && (
                        <span className="px-2 py-1 bg-primary/10 text-primary rounded-full text-xs">
                          {agent.configuration.agent_type}
                        </span>
                      )}
                    </div>
                  </CardContent>
                  <CardFooter className="border-t p-4 bg-muted/20 flex justify-between">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => navigate(`/agents/${agent.id}/edit`)}
                    >
                      <Settings className="h-4 w-4 mr-2" />
                      Configure
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => navigate(`/agents/${agent.id}`)}
                    >
                      Details
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </CardFooter>
                </Card>
              ))}
              
              <Card className="border-dashed flex items-center justify-center">
                <CardContent className="flex flex-col items-center justify-center p-6 text-center">
                  <PlusCircle className="h-12 w-12 text-muted-foreground mb-2" />
                  <h3 className="text-lg font-medium">Create New Agent</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Design a specialized research agent
                  </p>
                  <Button onClick={() => navigate("/agents/new")}>New Agent</Button>
                </CardContent>
              </Card>
            </div>
          )}
        </>
      )}
    </div>
  );
}
