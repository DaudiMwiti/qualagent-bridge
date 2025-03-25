
import { useState } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Download, Upload } from "lucide-react";

export default function DataManagement() {
  const { toast } = useToast();
  const [exportType, setExportType] = useState<string>("");
  const [exportFormat, setExportFormat] = useState<string>("");
  const [projectId, setProjectId] = useState<string>("");
  const [analysisId, setAnalysisId] = useState<string>("");
  
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    // Simulate file upload
    setTimeout(() => {
      toast({
        title: "File uploaded successfully",
        description: `${file.name} has been uploaded and is ready for analysis.`,
      });
      event.target.value = ""; // Reset file input
    }, 1500);
  };
  
  const handleExport = () => {
    // Validate form inputs
    if (!exportType) {
      toast({
        title: "Export failed",
        description: "Please select an export type",
        variant: "destructive",
      });
      return;
    }
    
    if (exportType === "project" && !projectId) {
      toast({
        title: "Export failed",
        description: "Please select a project to export",
        variant: "destructive",
      });
      return;
    }
    
    if (exportType === "analysis" && (!projectId || !analysisId)) {
      toast({
        title: "Export failed",
        description: "Please select both a project and analysis to export",
        variant: "destructive",
      });
      return;
    }
    
    // Simulate successful export
    toast({
      title: "Export successful",
      description: "Your data has been exported and is ready for download.",
    });
    
    // In a real app, this would redirect to the download URL or trigger browser download
  };
  
  return (
    <div>
      <PageHeader 
        title="Data Management" 
        description="Import and export data for your qualitative research"
      />
      
      <Tabs defaultValue="import" className="max-w-4xl">
        <TabsList className="mb-6">
          <TabsTrigger value="import">Import Data</TabsTrigger>
          <TabsTrigger value="export">Export Results</TabsTrigger>
        </TabsList>
        
        <TabsContent value="import">
          <Card>
            <CardHeader>
              <CardTitle>Import Research Data</CardTitle>
              <CardDescription>
                Upload data files for analysis in your projects
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="projectSelect">Select Project</Label>
                <Select onValueChange={setProjectId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Choose a project" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">Interview Study 2023</SelectItem>
                    <SelectItem value="2">Customer Feedback Analysis</SelectItem>
                    <SelectItem value="3">Research Survey Responses</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="fileUpload">Upload File</Label>
                <div className="grid gap-2">
                  <Input 
                    id="fileUpload" 
                    type="file" 
                    onChange={handleFileUpload}
                    accept=".txt,.csv,.docx,.pdf,.json"
                  />
                  <p className="text-xs text-muted-foreground">
                    Supported formats: TXT, CSV, DOCX, PDF, JSON (max 50MB)
                  </p>
                </div>
              </div>
              
              <div className="rounded-lg border border-dashed p-6 text-center">
                <div className="mx-auto flex max-w-[420px] flex-col items-center justify-center">
                  <Upload className="h-10 w-10 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-1">Drag & drop files</h3>
                  <p className="mb-4 text-sm text-muted-foreground text-center">
                    Drag and drop files here or click to browse your computer
                  </p>
                  <Button variant="secondary" size="sm">
                    Choose files
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="export">
          <Card>
            <CardHeader>
              <CardTitle>Export Analysis Results</CardTitle>
              <CardDescription>
                Download your analysis results in various formats
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="exportType">Export Type</Label>
                <Select onValueChange={setExportType}>
                  <SelectTrigger id="exportType">
                    <SelectValue placeholder="Select what to export" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="project">Full Project</SelectItem>
                    <SelectItem value="analysis">Single Analysis</SelectItem>
                    <SelectItem value="themes">Themes Only</SelectItem>
                    <SelectItem value="insights">Insights Only</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              {exportType && (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="projectSelect">Select Project</Label>
                    <Select onValueChange={setProjectId}>
                      <SelectTrigger id="projectSelect">
                        <SelectValue placeholder="Choose a project" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1">Interview Study 2023</SelectItem>
                        <SelectItem value="2">Customer Feedback Analysis</SelectItem>
                        <SelectItem value="3">Research Survey Responses</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  {(exportType === "analysis" || exportType === "themes" || exportType === "insights") && projectId && (
                    <div className="space-y-2">
                      <Label htmlFor="analysisSelect">Select Analysis</Label>
                      <Select onValueChange={setAnalysisId}>
                        <SelectTrigger id="analysisSelect">
                          <SelectValue placeholder="Choose an analysis" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="1">Thematic Analysis #1</SelectItem>
                          <SelectItem value="2">Sentiment Analysis #2</SelectItem>
                          <SelectItem value="3">Pattern Analysis #3</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  )}
                  
                  <div className="space-y-2">
                    <Label htmlFor="formatSelect">Export Format</Label>
                    <Select onValueChange={setExportFormat}>
                      <SelectTrigger id="formatSelect">
                        <SelectValue placeholder="Choose a format" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="csv">CSV</SelectItem>
                        <SelectItem value="json">JSON</SelectItem>
                        <SelectItem value="pdf">PDF Report</SelectItem>
                        <SelectItem value="xlsx">Excel (XLSX)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </>
              )}
            </CardContent>
            <CardFooter>
              <Button 
                className="w-full" 
                onClick={handleExport}
                disabled={!exportType || !projectId || (exportType !== "project" && !analysisId)}
              >
                <Download className="mr-2 h-4 w-4" />
                Export Data
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
