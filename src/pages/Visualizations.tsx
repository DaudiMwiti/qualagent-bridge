
import { useState } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { BarChart, PieChart, PieArcSeries, Cell, Legend, Pie, Tooltip, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from "recharts";

// Sample data for visualizations
const themeData = [
  { name: "User Experience", value: 42, fill: "#8884d8" },
  { name: "Performance", value: 28, fill: "#83a6ed" },
  { name: "Features", value: 15, fill: "#8dd1e1" },
  { name: "Pricing", value: 9, fill: "#82ca9d" },
  { name: "Support", value: 6, fill: "#a4de6c" }
];

const sentimentData = [
  { name: "Positive", value: 65, fill: "#82ca9d" },
  { name: "Neutral", value: 25, fill: "#83a6ed" },
  { name: "Negative", value: 10, fill: "#ff8042" }
];

const timeSeriesData = [
  { date: "Jan", positive: 30, negative: 10, neutral: 15 },
  { date: "Feb", positive: 25, negative: 12, neutral: 18 },
  { date: "Mar", positive: 35, negative: 8, neutral: 12 },
  { date: "Apr", positive: 40, negative: 5, neutral: 10 },
  { date: "May", positive: 45, negative: 4, neutral: 8 },
  { date: "Jun", positive: 50, negative: 6, neutral: 10 }
];

export default function Visualizations() {
  const [projectId, setProjectId] = useState<string>("");
  const [analysisId, setAnalysisId] = useState<string>("");
  
  const chartConfig = {
    positive: {
      label: "Positive",
      theme: {
        light: "#82ca9d",
        dark: "#82ca9d"
      }
    },
    negative: {
      label: "Negative",
      theme: {
        light: "#ff8042",
        dark: "#ff8042"
      }
    },
    neutral: {
      label: "Neutral",
      theme: {
        light: "#83a6ed",
        dark: "#83a6ed"
      }
    }
  };
  
  return (
    <div>
      <PageHeader 
        title="Visualizations" 
        description="Interactive visualizations of your analysis results"
      />
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-2">
              <Label htmlFor="projectSelect">Project</Label>
              <Select onValueChange={setProjectId}>
                <SelectTrigger id="projectSelect">
                  <SelectValue placeholder="Select project" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">Interview Study 2023</SelectItem>
                  <SelectItem value="2">Customer Feedback Analysis</SelectItem>
                  <SelectItem value="3">Research Survey Responses</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-2">
              <Label htmlFor="analysisSelect">Analysis</Label>
              <Select onValueChange={setAnalysisId} disabled={!projectId}>
                <SelectTrigger id="analysisSelect">
                  <SelectValue placeholder={projectId ? "Select analysis" : "Select a project first"} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">Thematic Analysis #1</SelectItem>
                  <SelectItem value="2">Sentiment Analysis #2</SelectItem>
                  <SelectItem value="3">Pattern Analysis #3</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>
      </div>
      
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="themes">Themes</TabsTrigger>
          <TabsTrigger value="sentiment">Sentiment</TabsTrigger>
          <TabsTrigger value="timeseries">Time Series</TabsTrigger>
        </TabsList>
        
        <TabsContent value="overview">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Theme Distribution</CardTitle>
                <CardDescription>
                  Key themes identified in your analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={themeData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        {themeData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Sentiment Analysis</CardTitle>
                <CardDescription>
                  Overall sentiment distribution in your data
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={sentimentData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        {sentimentData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        
        <TabsContent value="themes">
          <Card>
            <CardHeader>
              <CardTitle>Theme Analysis</CardTitle>
              <CardDescription>
                Detailed breakdown of themes identified in your data
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={themeData}
                    margin={{
                      top: 5,
                      right: 30,
                      left: 20,
                      bottom: 5,
                    }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="value" name="Frequency" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="sentiment">
          <Card>
            <CardHeader>
              <CardTitle>Sentiment Analysis</CardTitle>
              <CardDescription>
                Detailed sentiment breakdown of your qualitative data
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={sentimentData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={120}
                      fill="#8884d8"
                      paddingAngle={5}
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}`}
                    >
                      {sentimentData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="timeseries">
          <Card>
            <CardHeader>
              <CardTitle>Sentiment Over Time</CardTitle>
              <CardDescription>
                How sentiment has changed throughout your data collection
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-96">
                <ChartContainer config={chartConfig}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={timeSeriesData}
                      margin={{
                        top: 5,
                        right: 30,
                        left: 20,
                        bottom: 5,
                      }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <ChartTooltip 
                        content={<ChartTooltipContent />}
                      />
                      <Legend />
                      <Bar dataKey="positive" name="Positive" fill="#82ca9d" />
                      <Bar dataKey="neutral" name="Neutral" fill="#83a6ed" />
                      <Bar dataKey="negative" name="Negative" fill="#ff8042" />
                    </BarChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
