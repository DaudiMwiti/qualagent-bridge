
import { useState, useEffect } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { AlertCircle, CheckCircle, Info } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";

export default function AiProviderSettings() {
  const { toast } = useToast();
  
  // State for AI provider settings
  const [useOpenSourceEmbed, setUseOpenSourceEmbed] = useState(true);
  const [sentimentProvider, setSentimentProvider] = useState("hybrid");
  const [paramExtractionProvider, setParamExtractionProvider] = useState("openai");
  
  // Credentials state
  const [hfApiKey, setHfApiKey] = useState("");
  const [cohereApiKey, setCohereApiKey] = useState("");
  const [replicateApiToken, setReplicateApiToken] = useState("");
  const [symblApiKey, setSymblApiKey] = useState("");
  
  // Estimated cost and savings
  const [savingsPercent, setSavingsPercent] = useState(0);
  
  // Demo state
  const [isTestingProviders, setIsTestingProviders] = useState(false);
  const [testResults, setTestResults] = useState<any>(null);
  
  // Calculate estimated cost savings
  useEffect(() => {
    let savings = 0;
    
    // Embeddings savings (25% of cost)
    if (useOpenSourceEmbed) {
      savings += 25 * 0.65; // 65% savings on embeddings
    }
    
    // Sentiment savings (30% of cost)
    if (sentimentProvider === "hybrid" || sentimentProvider === "symbl") {
      savings += 30 * 0.75; // 75% savings on sentiment
    } else if (sentimentProvider === "huggingface") {
      savings += 30 * 0.90; // 90% savings on sentiment
    }
    
    // Parameter extraction savings (45% of cost)
    if (paramExtractionProvider === "mixtral") {
      savings += 45 * 0.60; // 60% savings on parameter extraction
    }
    
    setSavingsPercent(Math.round(savings));
  }, [useOpenSourceEmbed, sentimentProvider, paramExtractionProvider]);
  
  const handleSaveSettings = async () => {
    // In a real implementation, this would save to the backend
    toast({
      title: "Settings saved",
      description: "Your AI provider settings have been updated.",
      variant: "default",
    });
  };
  
  const handleTestProviders = async () => {
    setIsTestingProviders(true);
    
    // Simulate testing providers
    setTimeout(() => {
      setTestResults({
        embeddings: { 
          status: "success", 
          provider: useOpenSourceEmbed ? "HuggingFace (BGE-small)" : "OpenAI",
          latency: useOpenSourceEmbed ? "320ms" : "180ms"
        },
        sentiment: { 
          status: "success", 
          provider: 
            sentimentProvider === "openai" ? "OpenAI" : 
            sentimentProvider === "symbl" ? "Symbl.ai" :
            sentimentProvider === "huggingface" ? "HuggingFace" : "Hybrid",
          latency: sentimentProvider === "openai" ? "250ms" : "310ms"
        },
        extraction: { 
          status: "success", 
          provider: paramExtractionProvider === "mixtral" ? "Mixtral (Replicate)" : "OpenAI",
          latency: paramExtractionProvider === "mixtral" ? "1200ms" : "280ms"
        }
      });
      setIsTestingProviders(false);
    }, 2000);
  };
  
  return (
    <div className="container">
      <PageHeader
        title="AI Provider Settings"
        description="Configure hybrid AI architecture to optimize cost and performance"
      />
      
      <div className="grid gap-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <span>Estimated Cost Reduction</span>
            </CardTitle>
            <CardDescription>
              Based on your current settings, you are saving approximately:
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span>Cost Savings</span>
                <span className="font-bold text-lg">{savingsPercent}%</span>
              </div>
              <Progress value={savingsPercent} className="h-3" />
              
              <Alert className={savingsPercent >= 40 ? "bg-green-50 border-green-200" : "bg-yellow-50 border-yellow-200"}>
                <div className="flex items-center gap-2">
                  {savingsPercent >= 40 ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <Info className="h-5 w-5 text-yellow-500" />
                  )}
                  <AlertTitle>
                    {savingsPercent >= 40 ? "Target achieved" : "Target not reached"}
                  </AlertTitle>
                </div>
                <AlertDescription className="pl-7">
                  {savingsPercent >= 40 
                    ? "You've met the 40-60% cost reduction goal!" 
                    : "You need to enable more cost-saving options to reach the 40-60% target."}
                </AlertDescription>
              </Alert>
            </div>
          </CardContent>
        </Card>
        
        <Tabs defaultValue="providers">
          <TabsList className="grid grid-cols-2 mb-4">
            <TabsTrigger value="providers">Provider Settings</TabsTrigger>
            <TabsTrigger value="credentials">API Credentials</TabsTrigger>
          </TabsList>
          
          <TabsContent value="providers">
            <div className="grid gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Embedding Service</CardTitle>
                  <CardDescription>
                    Configure vector embeddings for document search and semantic retrieval
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="useOpenSourceEmbed">Use open-source embeddings</Label>
                      <p className="text-sm text-muted-foreground">
                        Use HuggingFace BGE-small-en instead of OpenAI
                      </p>
                    </div>
                    <Switch 
                      id="useOpenSourceEmbed" 
                      checked={useOpenSourceEmbed}
                      onCheckedChange={setUseOpenSourceEmbed}
                    />
                  </div>
                  
                  {useOpenSourceEmbed && (
                    <Alert variant="default" className="bg-blue-50 border-blue-200">
                      <Info className="h-4 w-4 text-blue-500" />
                      <AlertTitle>Cost Savings</AlertTitle>
                      <AlertDescription>
                        Using BAAI/bge-small-en can reduce embedding costs by up to 65%
                      </AlertDescription>
                    </Alert>
                  )}
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>Sentiment Analysis</CardTitle>
                  <CardDescription>
                    Configure sentiment analysis providers
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="sentimentProvider">Sentiment Provider</Label>
                    <Select 
                      value={sentimentProvider} 
                      onValueChange={setSentimentProvider}
                    >
                      <SelectTrigger id="sentimentProvider">
                        <SelectValue placeholder="Select provider" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="openai">OpenAI Only</SelectItem>
                        <SelectItem value="symbl">Symbl.ai</SelectItem>
                        <SelectItem value="huggingface">HuggingFace (Open-Source)</SelectItem>
                        <SelectItem value="hybrid">Hybrid (Smart Routing)</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-sm text-muted-foreground">
                      Hybrid mode uses Symbl.ai for simple sentiment and OpenAI for complex analysis
                    </p>
                  </div>
                  
                  {sentimentProvider !== "openai" && (
                    <Alert variant="default" className="bg-blue-50 border-blue-200">
                      <Info className="h-4 w-4 text-blue-500" />
                      <AlertTitle>Cost Savings</AlertTitle>
                      <AlertDescription>
                        {sentimentProvider === "hybrid" 
                          ? "Hybrid routing can reduce sentiment analysis costs by up to 75%" 
                          : sentimentProvider === "huggingface"
                            ? "Using open-source models can reduce sentiment costs by up to 90%"
                            : "Using Symbl.ai can reduce sentiment analysis costs by up to 75%"}
                      </AlertDescription>
                    </Alert>
                  )}
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>Parameter Extraction</CardTitle>
                  <CardDescription>
                    Configure parameter extraction for structured data
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="paramProvider">Parameter Extraction Provider</Label>
                    <Select 
                      value={paramExtractionProvider} 
                      onValueChange={setParamExtractionProvider}
                    >
                      <SelectTrigger id="paramProvider">
                        <SelectValue placeholder="Select provider" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="openai">OpenAI</SelectItem>
                        <SelectItem value="mixtral">Mixtral (via Replicate)</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-sm text-muted-foreground">
                      Mixtral is an open-source alternative with good parameter extraction capabilities
                    </p>
                  </div>
                  
                  {paramExtractionProvider !== "openai" && (
                    <Alert variant="default" className="bg-blue-50 border-blue-200">
                      <Info className="h-4 w-4 text-blue-500" />
                      <AlertTitle>Cost Savings</AlertTitle>
                      <AlertDescription>
                        Using Mixtral can reduce parameter extraction costs by up to 60%
                      </AlertDescription>
                    </Alert>
                  )}
                </CardContent>
              </Card>
              
              <div className="flex justify-end space-x-4">
                <Button 
                  variant="outline" 
                  onClick={handleTestProviders}
                  disabled={isTestingProviders}
                >
                  {isTestingProviders ? "Testing..." : "Test Providers"}
                </Button>
                <Button onClick={handleSaveSettings}>Save Settings</Button>
              </div>
              
              {testResults && (
                <Card>
                  <CardHeader>
                    <CardTitle>Provider Test Results</CardTitle>
                    <CardDescription>
                      Test results for your current provider configuration
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="font-medium">Embeddings</span>
                          <p className="text-sm text-muted-foreground">
                            Provider: {testResults.embeddings.provider}
                          </p>
                        </div>
                        <div className="flex items-center">
                          <span className="text-sm mr-2">{testResults.embeddings.latency}</span>
                          {testResults.embeddings.status === "success" ? (
                            <CheckCircle className="h-5 w-5 text-green-500" />
                          ) : (
                            <AlertCircle className="h-5 w-5 text-red-500" />
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="font-medium">Sentiment Analysis</span>
                          <p className="text-sm text-muted-foreground">
                            Provider: {testResults.sentiment.provider}
                          </p>
                        </div>
                        <div className="flex items-center">
                          <span className="text-sm mr-2">{testResults.sentiment.latency}</span>
                          {testResults.sentiment.status === "success" ? (
                            <CheckCircle className="h-5 w-5 text-green-500" />
                          ) : (
                            <AlertCircle className="h-5 w-5 text-red-500" />
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="font-medium">Parameter Extraction</span>
                          <p className="text-sm text-muted-foreground">
                            Provider: {testResults.extraction.provider}
                          </p>
                        </div>
                        <div className="flex items-center">
                          <span className="text-sm mr-2">{testResults.extraction.latency}</span>
                          {testResults.extraction.status === "success" ? (
                            <CheckCircle className="h-5 w-5 text-green-500" />
                          ) : (
                            <AlertCircle className="h-5 w-5 text-red-500" />
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>
          
          <TabsContent value="credentials">
            <Card>
              <CardHeader>
                <CardTitle>API Credentials</CardTitle>
                <CardDescription>
                  Configure API keys for third-party AI services
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="hfApiKey">HuggingFace API Key</Label>
                  <input 
                    id="hfApiKey"
                    type="password"
                    value={hfApiKey}
                    onChange={(e) => setHfApiKey(e.target.value)}
                    className="w-full p-2 border rounded-md"
                    placeholder="hf_..."
                  />
                  <p className="text-sm text-muted-foreground">
                    Required for HuggingFace Inference API (embeddings and sentiment)
                  </p>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="cohereApiKey">Cohere API Key</Label>
                  <input 
                    id="cohereApiKey"
                    type="password"
                    value={cohereApiKey}
                    onChange={(e) => setCohereApiKey(e.target.value)}
                    className="w-full p-2 border rounded-md"
                    placeholder="..."
                  />
                  <p className="text-sm text-muted-foreground">
                    Optional fallback for embeddings
                  </p>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="replicateApiToken">Replicate API Token</Label>
                  <input 
                    id="replicateApiToken"
                    type="password"
                    value={replicateApiToken}
                    onChange={(e) => setReplicateApiToken(e.target.value)}
                    className="w-full p-2 border rounded-md"
                    placeholder="r8_..."
                  />
                  <p className="text-sm text-muted-foreground">
                    Required for Mixtral parameter extraction
                  </p>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="symblApiKey">Symbl.ai API Key</Label>
                  <input 
                    id="symblApiKey"
                    type="password"
                    value={symblApiKey}
                    onChange={(e) => setSymblApiKey(e.target.value)}
                    className="w-full p-2 border rounded-md"
                    placeholder="..."
                  />
                  <p className="text-sm text-muted-foreground">
                    Required for Symbl.ai sentiment analysis
                  </p>
                </div>
                
                <Alert variant="default" className="mt-4">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>API Keys Security</AlertTitle>
                  <AlertDescription>
                    API keys are stored securely and never shared with third parties. 
                    Keys are used only for the specified API calls.
                  </AlertDescription>
                </Alert>
                
                <div className="flex justify-end pt-4">
                  <Button onClick={handleSaveSettings}>Save Credentials</Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
