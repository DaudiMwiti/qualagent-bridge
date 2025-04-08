
import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/status-badge";
import { AnalysisStream } from "@/components/analysis/analysis-stream";
import { Download, ClipboardList, FileText, BarChart, Brain, Tag, Copy, Archive, Link as LinkIcon } from "lucide-react";
import { useProject } from "@/api/projects";
import { useAnalysis, useAnalysisResults, AnalysisResults } from "@/api/analysis";
import { useToast } from "@/hooks/use-toast";

export default function AnalysisDetail() {
  const { projectId, analysisId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const projId = projectId ? parseInt(projectId) : 0;
  const analyId = analysisId ? parseInt(analysisId) : 0;
  
  const { data: project } = useProject(projId);
  const { data: analysis, isLoading: isLoadingAnalysis } = useAnalysis(analyId);
  const { data: resultsData, isLoading: isLoadingResults } = useAnalysisResults(
    analyId, 
    analysis?.status || ""
  );
  
  const [activeTab, setActiveTab] = useState("overview");
  const [results, setResults] = useState<AnalysisResults | null>(null);
  
  // Set results either from SSE stream or from API fetch
  useEffect(() => {
    if (resultsData) {
      setResults(resultsData);
    }
  }, [resultsData]);
  
  const handleStreamComplete = (streamResults: AnalysisResults) => {
    setResults(streamResults);
  };
  
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copied to clipboard",
      description: "Text has been copied to your clipboard",
    });
  };
  
  if (isLoadingAnalysis) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-8 bg-muted rounded w-1/4" />
        <div className="h-4 bg-muted rounded w-1/3" />
        <div className="h-[400px] bg-muted rounded" />
      </div>
    );
  }
  
  if (!analysis || !project) {
    return (
      <div className="text-center p-12">
        <h2 className="text-xl font-semibold mb-2">Analysis not found</h2>
        <p className="text-muted-foreground mb-4">The analysis you're looking for doesn't exist or has been deleted.</p>
        <Button onClick={() => navigate("/projects")}>Back to Projects</Button>
      </div>
    );
  }
  
  // Prepare display of results based on status
  const isCompleted = analysis.status === "completed";
  const isFailed = analysis.status === "failed";
  const isInProgress = analysis.status === "in_progress";
  const isPending = analysis.status === "pending";
  
  return (
    <div>
      <PageHeader 
        title={`Analysis #${analysis.id}`} 
        description={`Analysis for Project: ${project.name}`}
        breadcrumbs={[
          { label: "Projects", href: "/projects" },
          { label: project.name, href: `/projects/${project.id}` },
          { label: `Analysis #${analysis.id}`, href: `/projects/${project.id}/analysis/${analysis.id}` },
        ]}
        actions={
          isCompleted && (
            <Button>
              <Download className="mr-2 h-4 w-4" />
              Export Results
            </Button>
          )
        }
      />
      
      <div className="flex items-center mb-6">
        <div className="flex items-center text-sm text-muted-foreground mr-6">
          <ClipboardList className="h-4 w-4 mr-2" />
          Created: {new Date(analysis.created_at).toLocaleString()}
        </div>
        
        {analysis.completed_at && (
          <div className="flex items-center text-sm text-muted-foreground mr-6">
            <FileText className="h-4 w-4 mr-2" />
            Completed: {new Date(analysis.completed_at).toLocaleString()}
          </div>
        )}
        
        <StatusBadge status={analysis.status} className="ml-auto" />
      </div>
      
      {(isInProgress || isPending) && (
        <AnalysisStream 
          analysisId={analysis.id} 
          onComplete={handleStreamComplete}
        />
      )}
      
      {isFailed && (
        <Card className="mb-6 border-destructive">
          <CardHeader className="bg-destructive/10 text-destructive">
            <CardTitle className="text-lg">Analysis Failed</CardTitle>
          </CardHeader>
          <CardContent className="pt-4">
            <p>{analysis.data.error || "An unknown error occurred during analysis."}</p>
          </CardContent>
        </Card>
      )}
      
      {isCompleted && results && (
        <Tabs value={activeTab} onValueChange={setActiveTab} className="mt-6">
          <TabsList className="mb-6">
            <TabsTrigger value="overview">
              <FileText className="h-4 w-4 mr-2" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="themes">
              <Tag className="h-4 w-4 mr-2" />
              Themes
            </TabsTrigger>
            <TabsTrigger value="insights">
              <Brain className="h-4 w-4 mr-2" />
              Insights
            </TabsTrigger>
            {results.memory_used && results.memory_used.length > 0 && (
              <TabsTrigger value="memory">
                <Archive className="h-4 w-4 mr-2" />
                Context Used
              </TabsTrigger>
            )}
            {results.sentiment && (
              <TabsTrigger value="sentiment">
                <BarChart className="h-4 w-4 mr-2" />
                Sentiment
              </TabsTrigger>
            )}
          </TabsList>
          
          <TabsContent value="overview">
            <Card>
              <CardHeader>
                <CardTitle>Analysis Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="relative">
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className="absolute top-0 right-0"
                    onClick={() => results.summary && copyToClipboard(results.summary)}
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                  <p className="prose max-w-none">{results.summary}</p>
                </div>
                
                <h3 className="text-lg font-medium mt-6 mb-3">Key Metrics</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card>
                    <CardContent className="pt-6">
                      <div className="text-center">
                        <div className="text-3xl font-bold">{results.themes?.length || 0}</div>
                        <p className="text-sm text-muted-foreground">Themes Identified</p>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="pt-6">
                      <div className="text-center">
                        <div className="text-3xl font-bold">{results.insights?.length || 0}</div>
                        <p className="text-sm text-muted-foreground">Key Insights</p>
                      </div>
                    </CardContent>
                  </Card>
                  
                  {results.sentiment && (
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-center">
                          <div className="text-3xl font-bold">{results.sentiment.overall}</div>
                          <p className="text-sm text-muted-foreground">Overall Sentiment</p>
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="themes">
            <div className="space-y-6">
              {results.themes?.length ? (
                results.themes.map((theme, index) => (
                  <Card key={index}>
                    <CardHeader>
                      <CardTitle className="text-lg">{theme.name}</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <p>{theme.description}</p>
                      
                      {theme.keywords?.length > 0 && (
                        <div>
                          <h4 className="font-medium mb-2">Keywords</h4>
                          <div className="flex flex-wrap gap-2">
                            {theme.keywords.map((keyword, i) => (
                              <span 
                                key={i}
                                className="px-2 py-1 bg-primary/10 text-primary rounded-full text-xs"
                              >
                                {keyword}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {theme.quotes?.length > 0 && (
                        <div>
                          <h4 className="font-medium mb-2">Supporting Quotes</h4>
                          <div className="space-y-2">
                            {theme.quotes.map((quote, i) => (
                              <div 
                                key={i}
                                className="bg-muted p-3 rounded-md text-sm border-l-4 border-primary"
                              >
                                <p>"{typeof quote === 'string' ? quote : quote.text}"</p>
                                
                                {typeof quote !== 'string' && quote.source && (
                                  <div className="mt-2 flex items-center text-xs text-muted-foreground pt-2 border-t border-muted">
                                    <LinkIcon className="h-3 w-3 mr-1" />
                                    <p>
                                      Source: {quote.source.metadata?.filename || quote.source.document_id || 'Unknown'} 
                                      {quote.source.chunk_id !== undefined && ` (chunk ${quote.source.chunk_id})`}
                                    </p>
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))
              ) : (
                <div className="text-center p-12 border rounded-md">
                  <h3 className="text-lg font-medium mb-2">No themes identified</h3>
                  <p className="text-muted-foreground">
                    The analysis didn't detect any specific themes in the data.
                  </p>
                </div>
              )}
            </div>
          </TabsContent>
          
          <TabsContent value="insights">
            <Card>
              <CardHeader>
                <CardTitle>Key Insights</CardTitle>
              </CardHeader>
              <CardContent>
                {results.insights?.length ? (
                  <div className="space-y-4">
                    {results.insights.map((insight, index) => (
                      <div key={index} className="relative p-4 bg-muted/30 rounded-md">
                        <Button 
                          variant="ghost" 
                          size="icon" 
                          className="absolute top-2 right-2"
                          onClick={() => copyToClipboard(typeof insight === 'string' ? insight : JSON.stringify(insight))}
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                        
                        {typeof insight === 'string' ? (
                          <p className="pr-8">{insight}</p>
                        ) : (
                          <div className="pr-8">
                            <h4 className="font-medium mb-2">{insight.theme}</h4>
                            {insight.quote && (
                              <blockquote className="pl-4 border-l-2 border-primary/50 italic mb-2">
                                "{insight.quote}"
                              </blockquote>
                            )}
                            <p>{insight.summary}</p>
                            
                            {insight.source && (
                              <div className="mt-2 flex items-center text-xs text-muted-foreground pt-2 border-t border-muted">
                                <LinkIcon className="h-3 w-3 mr-1" />
                                <p>
                                  Source: {insight.source.metadata?.filename || insight.source.document_id || 'Unknown'} 
                                  {insight.source.chunk_id !== undefined && ` (chunk ${insight.source.chunk_id})`}
                                </p>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center p-6">
                    <p className="text-muted-foreground">
                      No specific insights were generated from this analysis.
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
          
          {/* Context Used Tab */}
          <TabsContent value="memory">
            <Card>
              <CardHeader>
                <CardTitle>Context Used</CardTitle>
                <p className="text-sm text-muted-foreground">
                  These memories from previous analyses were used to inform this analysis.
                </p>
              </CardHeader>
              <CardContent>
                {results.memory_used?.length ? (
                  <div className="space-y-4">
                    {results.memory_used.map((memory, index) => (
                      <Card key={index} className="border border-muted">
                        <CardContent className="pt-6 space-y-2">
                          <div className="flex justify-between mb-2">
                            <span className="inline-block px-2 py-1 text-xs rounded bg-primary/10 text-primary">
                              {memory.memory_type}
                            </span>
                            {memory.timestamp && (
                              <span className="text-xs text-muted-foreground">
                                {new Date(memory.timestamp * 1000).toLocaleString()}
                              </span>
                            )}
                          </div>
                          {memory.tag && (
                            <p className="text-xs font-medium">Tag: {memory.tag}</p>
                          )}
                          <blockquote className="text-sm border-l-4 border-primary pl-4 py-1 italic">
                            {memory.text}
                          </blockquote>
                          {memory.score !== undefined && (
                            <div className="mt-2">
                              <p className="text-xs text-muted-foreground">
                                Relevance Score: 
                                <span className="font-medium ml-1">
                                  {(memory.score * 100).toFixed(1)}%
                                </span>
                              </p>
                              <div className="w-full h-1.5 bg-muted rounded-full mt-1">
                                <div 
                                  className="h-full bg-primary rounded-full" 
                                  style={{ width: `${memory.score * 100}%` }}
                                />
                              </div>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                ) : (
                  <div className="text-center p-6">
                    <p className="text-muted-foreground">
                      No prior memories were used as context for this analysis.
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
          
          {results.sentiment && (
            <TabsContent value="sentiment">
              <Card>
                <CardHeader>
                  <CardTitle>Sentiment Analysis</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center mb-6">
                    <div className="text-4xl font-bold mb-1">{results.sentiment.overall}</div>
                    <p className="text-muted-foreground">Overall Sentiment</p>
                  </div>
                  
                  <div className="w-full h-8 rounded-full overflow-hidden bg-muted mb-8">
                    <div 
                      className="h-full bg-gradient-to-r from-red-500 via-yellow-500 to-green-500"
                      style={{ 
                        width: `${((results.sentiment.score + 1) / 2) * 100}%` 
                      }}
                    />
                  </div>
                  
                  {results.sentiment.breakdown && (
                    <div>
                      <h3 className="font-medium mb-4">Sentiment Breakdown</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {Object.entries(results.sentiment.breakdown).map(([category, value]) => (
                          <div key={category} className="p-4 border rounded-md">
                            <div className="font-medium capitalize mb-2">{category}</div>
                            <div className="flex items-center">
                              <div className="w-full h-4 rounded-full overflow-hidden bg-muted">
                                <div 
                                  className={`h-full ${typeof value === 'number' 
                                    ? value > 0 
                                      ? 'bg-green-500' 
                                      : value < 0 
                                        ? 'bg-red-500' 
                                        : 'bg-yellow-500'
                                    : 'bg-blue-500'
                                  }`}
                                  style={{ 
                                    width: `${typeof value === 'number' ? Math.abs(value) * 100 : 50}%` 
                                  }}
                                />
                              </div>
                              <span className="ml-2 text-sm">
                                {typeof value === 'number' 
                                  ? value.toFixed(2) 
                                  : value}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          )}
        </Tabs>
      )}
    </div>
  );
}
