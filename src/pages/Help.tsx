
import { useState } from "react";
import { PageHeader } from "@/components/ui/page-header";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { HelpCircle, Search } from "lucide-react";

export default function Help() {
  const [searchQuery, setSearchQuery] = useState("");
  
  const faqItems = [
    {
      question: "How do I create a new analysis?",
      answer: "To create a new analysis, navigate to your project details page and click the 'New Analysis' button. Follow the steps to select your analysis type, upload data, and configure the agent for analysis."
    },
    {
      question: "What types of data can I import?",
      answer: "QualAgents supports various data formats including CSV, TXT, DOC/DOCX, and PDF files. You can also directly paste text for analysis. For interview transcripts, we recommend using consistent formatting for best results."
    },
    {
      question: "How long does an analysis take to complete?",
      answer: "Analysis time depends on the amount of data and complexity of the analysis. Most analyses complete within a few minutes. You'll receive a notification when your analysis is complete, and you can always check the status in your project dashboard."
    },
    {
      question: "Can I customize the analysis agents?",
      answer: "Yes, you can customize the analysis agents through the agent configuration page. You can adjust parameters like level of detail, focus areas, and the type of insights you want to generate from your data."
    },
    {
      question: "How do I export my analysis results?",
      answer: "From any completed analysis, click the 'Export' button to download your results. You can choose between various formats including PDF, CSV, and JSON formats depending on your needs."
    }
  ];
  
  // Filter FAQ items based on search query
  const filteredFaqItems = searchQuery 
    ? faqItems.filter(item => 
        item.question.toLowerCase().includes(searchQuery.toLowerCase()) || 
        item.answer.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : faqItems;
  
  return (
    <div>
      <PageHeader 
        title="Help & Documentation" 
        description="Learn how to use QualAgents for qualitative research"
        icon={HelpCircle}
      />
      
      <div className="mb-8">
        <div className="max-w-md mx-auto mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input
              type="search"
              placeholder="Search help topics..."
              className="pl-10"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
      </div>
      
      <Tabs defaultValue="faq" className="max-w-4xl mx-auto">
        <TabsList className="mb-6">
          <TabsTrigger value="faq">Frequently Asked Questions</TabsTrigger>
          <TabsTrigger value="guides">User Guides</TabsTrigger>
          <TabsTrigger value="api">API Documentation</TabsTrigger>
        </TabsList>
        
        <TabsContent value="faq">
          <Card>
            <CardHeader>
              <CardTitle>Frequently Asked Questions</CardTitle>
              <CardDescription>
                Common questions and answers about using QualAgents
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Accordion type="single" collapsible className="w-full">
                {filteredFaqItems.length > 0 ? (
                  filteredFaqItems.map((item, index) => (
                    <AccordionItem key={index} value={`item-${index}`}>
                      <AccordionTrigger>{item.question}</AccordionTrigger>
                      <AccordionContent>
                        <p className="text-muted-foreground">{item.answer}</p>
                      </AccordionContent>
                    </AccordionItem>
                  ))
                ) : (
                  <div className="py-4 text-center text-muted-foreground">
                    No results found for "{searchQuery}"
                  </div>
                )}
              </Accordion>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="guides">
          <Card>
            <CardHeader>
              <CardTitle>User Guides</CardTitle>
              <CardDescription>
                Step-by-step guides to help you make the most of QualAgents
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base">Getting Started Guide</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground mb-4">
                      Learn the basics of setting up your first project and running analyses.
                    </p>
                    <Button variant="outline" size="sm">View Guide</Button>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base">Advanced Analysis Techniques</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground mb-4">
                      Discover advanced features for deeper insights from your qualitative data.
                    </p>
                    <Button variant="outline" size="sm">View Guide</Button>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base">Data Import & Export</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground mb-4">
                      Learn how to import your research data and export analysis results.
                    </p>
                    <Button variant="outline" size="sm">View Guide</Button>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base">Agent Configuration</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground mb-4">
                      Configure AI agents to match your specific research methodology.
                    </p>
                    <Button variant="outline" size="sm">View Guide</Button>
                  </CardContent>
                </Card>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="api">
          <Card>
            <CardHeader>
              <CardTitle>API Documentation</CardTitle>
              <CardDescription>
                Resources for developers integrating with the QualAgents API
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-6">
                <p className="text-muted-foreground mb-4">
                  QualAgents provides a RESTful API that allows you to integrate our analysis capabilities into your own applications.
                </p>
                <Button>View API Reference</Button>
              </div>
              
              <div className="border rounded-md p-4 bg-muted/30">
                <h3 className="text-sm font-medium mb-2">Example API Request</h3>
                <pre className="text-xs bg-muted p-3 rounded overflow-x-auto">
{`POST /api/v1/analysis
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
  "project_id": 123,
  "agent_id": 456,
  "data": {
    "text": "Your qualitative data for analysis"
  }
}`}
                </pre>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
