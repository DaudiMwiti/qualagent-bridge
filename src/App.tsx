
import { Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "@/components/ui/toaster";
import { AppLayout } from "@/components/layout/app-layout";
import Dashboard from "@/pages/Dashboard";
import Projects from "@/pages/Projects";
import ProjectDetail from "@/pages/ProjectDetail";
import NewProject from "@/pages/NewProject";
import Agents from "@/pages/Agents";
import Settings from "@/pages/Settings";
import NotFound from "@/pages/NotFound";
import NewAnalysis from "@/pages/NewAnalysis";
import AnalysisDetail from "@/pages/AnalysisDetail";
import LandingPage from "@/pages/LandingPage";
import Help from "@/pages/Help";
import DataManagement from "@/pages/DataManagement";
import Visualizations from "@/pages/Visualizations";

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        
        <Route path="/dashboard" element={<AppLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="projects" element={<Projects />} />
          <Route path="projects/new" element={<NewProject />} />
          <Route path="projects/:projectId" element={<ProjectDetail />} />
          <Route path="projects/:projectId/analysis/new" element={<NewAnalysis />} />
          <Route path="projects/:projectId/analysis/:analysisId" element={<AnalysisDetail />} />
          <Route path="agents" element={<Agents />} />
          <Route path="settings" element={<Settings />} />
          <Route path="help" element={<Help />} />
          <Route path="data" element={<DataManagement />} />
          <Route path="visualizations" element={<Visualizations />} />
        </Route>
        
        <Route path="*" element={<NotFound />} />
      </Routes>
      <Toaster />
    </>
  );
}

export default App;
