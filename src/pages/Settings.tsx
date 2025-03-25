
import { useState } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { useToast } from "@/hooks/use-toast";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart } from "lucide-react";

export default function Settings() {
  const { toast } = useToast();
  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window !== "undefined") {
      return document.documentElement.classList.contains("dark");
    }
    return false;
  });
  
  const toggleDarkMode = () => {
    const newDarkMode = !darkMode;
    setDarkMode(newDarkMode);
    
    if (newDarkMode) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  };
  
  const saveOpenAIKey = (key: string) => {
    // In a real app, you would save this to a secure storage
    localStorage.setItem("openai_api_key", key);
    
    toast({
      title: "API Key Saved",
      description: "Your OpenAI API key has been saved successfully",
    });
  };
  
  return (
    <div>
      <PageHeader 
        title="Settings" 
        description="Configure your application preferences"
      />
      
      <div className="grid gap-6 max-w-2xl">
        <Card>
          <CardHeader>
            <CardTitle>OpenAI Configuration</CardTitle>
            <CardDescription>
              Configure your OpenAI API key for qualitative analysis
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="apiKey">OpenAI API Key</Label>
              <div className="flex space-x-2">
                <Input
                  id="apiKey"
                  type="password"
                  placeholder="sk-..."
                  onChange={(e) => {
                    // Store value temporarily but don't set in state for security
                    e.target.dataset.value = e.target.value;
                  }}
                />
                <Button onClick={() => {
                  const input = document.getElementById('apiKey') as HTMLInputElement;
                  const key = input?.dataset.value || '';
                  saveOpenAIKey(key);
                  input.value = '';
                }}>Save</Button>
              </div>
              <p className="text-sm text-muted-foreground">
                Your API key is stored locally and not sent to our servers
              </p>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Appearance</CardTitle>
            <CardDescription>
              Customize how the application looks
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="darkMode">Dark Mode</Label>
                <p className="text-sm text-muted-foreground">
                  Switch between light and dark themes
                </p>
              </div>
              <Switch 
                id="darkMode" 
                checked={darkMode}
                onCheckedChange={toggleDarkMode}
              />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Analysis Preferences</CardTitle>
            <CardDescription>
              Configure your research workflow preferences
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="streamResults">Stream Analysis Results</Label>
                <p className="text-sm text-muted-foreground">
                  Show real-time updates during analysis
                </p>
              </div>
              <Switch id="streamResults" defaultChecked />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="memoryEnabled">Agent Memory</Label>
                <p className="text-sm text-muted-foreground">
                  Enable agents to remember context from previous analyses
                </p>
              </div>
              <Switch id="memoryEnabled" defaultChecked />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="visualizationEnabled">Data Visualization</Label>
                <p className="text-sm text-muted-foreground">
                  Create charts and graphs from analysis results
                </p>
              </div>
              <Switch id="visualizationEnabled" defaultChecked />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
