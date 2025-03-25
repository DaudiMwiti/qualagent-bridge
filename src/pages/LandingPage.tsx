
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { 
  BrainCircuit, 
  LineChart, 
  SearchCheck, 
  MessagesSquare, 
  Sparkles, 
  Database,
  ArrowRight, 
  Upload, 
  Bot, 
  Lightbulb,
  Github
} from "lucide-react";

export default function LandingPage() {
  const navigate = useNavigate();

  // Initialize theme on component mount
  useEffect(() => {
    // Check and set preferred color scheme
    if (localStorage.getItem("theme") === "dark" || 
        (!localStorage.getItem("theme") && window.matchMedia("(prefers-color-scheme: dark)").matches)) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      {/* Hero Section */}
      <header className="w-full py-16 md:py-24 px-4 bg-gradient-to-br from-background to-secondary/20">
        <div className="container mx-auto max-w-6xl">
          <div className="flex flex-col items-center text-center">
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-4">
              Unlock Insights from Qualitative Research
            </h1>
            <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mb-8">
              QualAgents combines AI-powered analysis with intuitive design to transform your 
              qualitative data into actionable insights.
            </p>
            <Button 
              size="lg" 
              onClick={() => navigate("/dashboard")}
              className="group text-lg px-8"
            >
              Get Started
              <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
            </Button>
          </div>
        </div>
      </header>

      {/* How It Works Section */}
      <section className="py-16 md:py-24 px-4 bg-background">
        <div className="container mx-auto max-w-6xl">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">
            How It Works
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
            {/* Step 1 */}
            <div className="flex flex-col items-center text-center">
              <div className="w-16 h-16 flex items-center justify-center rounded-full bg-primary/10 text-primary mb-4">
                <Upload className="h-8 w-8" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Upload Your Data</h3>
              <p className="text-muted-foreground">
                Import interview transcripts, survey responses, or any text-based research data.
              </p>
            </div>
            
            {/* Step 2 */}
            <div className="flex flex-col items-center text-center">
              <div className="w-16 h-16 flex items-center justify-center rounded-full bg-primary/10 text-primary mb-4">
                <Bot className="h-8 w-8" />
              </div>
              <h3 className="text-xl font-semibold mb-2">AI Analysis</h3>
              <p className="text-muted-foreground">
                Our specialized AI agents process and analyze your qualitative data with advanced NLP.
              </p>
            </div>
            
            {/* Step 3 */}
            <div className="flex flex-col items-center text-center">
              <div className="w-16 h-16 flex items-center justify-center rounded-full bg-primary/10 text-primary mb-4">
                <Lightbulb className="h-8 w-8" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Discover Insights</h3>
              <p className="text-muted-foreground">
                Review visualized themes, patterns, and insights derived from your research.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Key Features */}
      <section className="py-16 md:py-24 px-4 bg-secondary/20">
        <div className="container mx-auto max-w-6xl">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">
            Key Features
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <Card className="border-none shadow-md">
              <CardContent className="pt-6">
                <div className="flex items-start gap-4">
                  <div className="mt-1 text-primary">
                    <BrainCircuit className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">AI-Powered Analysis</h3>
                    <p className="text-muted-foreground">
                      Advanced language models analyze text data to identify themes, sentiments, and patterns.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Feature 2 */}
            <Card className="border-none shadow-md">
              <CardContent className="pt-6">
                <div className="flex items-start gap-4">
                  <div className="mt-1 text-primary">
                    <SearchCheck className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">Theme Clustering</h3>
                    <p className="text-muted-foreground">
                      Automatically group similar concepts and themes for faster insight generation.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Feature 3 */}
            <Card className="border-none shadow-md">
              <CardContent className="pt-6">
                <div className="flex items-start gap-4">
                  <div className="mt-1 text-primary">
                    <MessagesSquare className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">Semantic Search</h3>
                    <p className="text-muted-foreground">
                      Find relevant insights and data points using natural language queries.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Feature 4 */}
            <Card className="border-none shadow-md">
              <CardContent className="pt-6">
                <div className="flex items-start gap-4">
                  <div className="mt-1 text-primary">
                    <LineChart className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">Visual Reporting</h3>
                    <p className="text-muted-foreground">
                      Interactive dashboards and visualizations make complex findings easy to understand.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Feature 5 */}
            <Card className="border-none shadow-md">
              <CardContent className="pt-6">
                <div className="flex items-start gap-4">
                  <div className="mt-1 text-primary">
                    <Database className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">Memory Systems</h3>
                    <p className="text-muted-foreground">
                      Persistent memory allows agents to build contextual understanding across analyses.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Feature 6 */}
            <Card className="border-none shadow-md">
              <CardContent className="pt-6">
                <div className="flex items-start gap-4">
                  <div className="mt-1 text-primary">
                    <Sparkles className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">Customizable Agents</h3>
                    <p className="text-muted-foreground">
                      Tailor AI agents to your specific research domains and methodologies.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Screenshot Placeholder */}
      <section className="py-16 md:py-24 px-4 bg-background">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              See QualAgents in Action
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Our intuitive interface makes qualitative research analysis simple and powerful.
            </p>
          </div>
          
          <div className="bg-gradient-to-r from-primary/5 to-secondary/10 aspect-video rounded-xl border shadow-md flex items-center justify-center">
            <p className="text-muted-foreground text-xl">UI Screenshot Placeholder</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto py-12 bg-muted/40">
        <div className="container mx-auto max-w-6xl px-4">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center">
              <BrainCircuit className="h-6 w-6 text-primary mr-2" />
              <span className="text-xl font-semibold">QualAgents</span>
            </div>
            
            <div className="flex flex-wrap gap-8 items-center justify-center">
              <a href="#" className="text-muted-foreground hover:text-foreground transition-colors">
                About
              </a>
              <a href="#" className="text-muted-foreground hover:text-foreground transition-colors flex items-center gap-2">
                <Github className="h-4 w-4" />
                GitHub
              </a>
              <a href="#" className="text-muted-foreground hover:text-foreground transition-colors">
                Contact
              </a>
            </div>
            
            <div className="text-sm text-muted-foreground">
              © {new Date().getFullYear()} QualAgents. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
