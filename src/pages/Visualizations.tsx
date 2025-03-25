
import { useState } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { 
  CartesianGrid, Legend, Line, LineChart, Pie, PieChart, ResponsiveContainer, 
  Tooltip, XAxis, YAxis, BarChart, Bar, Cell
} from "recharts";
import { BarChart as BarChartIcon } from "lucide-react";

// Sample data for visualization
const themeData = [
  { name: "Communication", value: 35 },
  { name: "User Experience", value: 28 },
  { name: "Functionality", value: 22 },
  { name: "Performance", value: 15 },
  { name: "Other", value: 10 },
];

const sentimentData = [
  { name: "Jan", positive: 30, negative: 10, neutral: 15 },
  { name: "Feb", positive: 25, negative: 12, neutral: 18 },
  { name: "Mar", positive: 35, negative: 8, neutral: 12 },
  { name: "Apr", positive: 40, negative: 5, neutral: 10 },
  { name: "May", positive: 32, negative: 15, neutral: 8 },
  { name: "Jun", positive: 38, negative: 10, neutral: 7 },
];

const insightTrendData = [
  { month: "Jan", insights: 5 },
  { month: "Feb", insights: 8 },
  { month: "Mar", insights: 12 },
  { month: "Apr", insights: 15 },
  { month: "May", insights: 18 },
  { month: "Jun", insights: 20 },
];

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#9370DB'];

export default function Visualizations() {
  const [projectId, setProjectId] = useState<string>("");
  const [analysisId, setAnalysisId] = useState<string>("");
  
  return (
    <div>
      <PageHeader 
        title="Visualizations" 
        description="Interactive visualizations of your research data"
      />
      
      <div className="mb-6 space-y-4 max-w-4xl">
        <div className="grid gap-4 sm:grid-cols-2">
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
          
          {projectId && (
            <div className="space-y-2">
              <Label htmlFor="analysisSelect">Analysis</Label>
              <Select onValueChange={setAnalysisId}>
                <SelectTrigger id="analysisSelect">
                  <SelectValue placeholder="Select analysis" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">Thematic Analysis #1</SelectItem>
                  <SelectItem value="2">Sentiment Analysis #2</SelectItem>
                  <SelectItem value="3">Pattern Analysis #3</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}
        </div>
      </div>
      
      <Tabs defaultValue="themes" className="max-w-4xl">
        <TabsList className="mb-6">
          <TabsTrigger value="themes">Themes</TabsTrigger>
          <TabsTrigger value="sentiment">Sentiment Analysis</TabsTrigger>
          <TabsTrigger value="insights">Insights Over Time</TabsTrigger>
        </TabsList>
        
        <TabsContent value="themes">
          <Card>
            <CardHeader>
              <CardTitle>Theme Distribution</CardTitle>
              <CardDescription>
                Visualization of key themes identified in your qualitative data
              </CardDescription>
            </CardHeader>
            <CardContent className="h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={themeData}
                    cx="50%"
                    cy="50%"
                    labelLine={true}
                    outerRadius={130}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {themeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="sentiment">
          <Card>
            <CardHeader>
              <CardTitle>Sentiment Analysis Over Time</CardTitle>
              <CardDescription>
                Tracking positive, negative, and neutral sentiment
              </CardDescription>
            </CardHeader>
            <CardContent className="h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={sentimentData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="positive" stroke="#00C49F" activeDot={{ r: 8 }} />
                  <Line type="monotone" dataKey="negative" stroke="#FF8042" />
                  <Line type="monotone" dataKey="neutral" stroke="#0088FE" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="insights">
          <Card>
            <CardHeader>
              <CardTitle>Insights Generated Over Time</CardTitle>
              <CardDescription>
                Tracking the accumulation of research insights
              </CardDescription>
            </CardHeader>
            <CardContent className="h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={insightTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="insights" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
