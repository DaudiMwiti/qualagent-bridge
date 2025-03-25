
import { useEffect, useState, useRef } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/status-badge";
import { Analysis, AnalysisResults } from "@/api/analysis";

interface AnalysisStreamProps {
  analysisId: number;
  onComplete?: (results: AnalysisResults) => void;
}

export function AnalysisStream({ analysisId, onComplete }: AnalysisStreamProps) {
  const [status, setStatus] = useState<string>("connecting");
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const eventSourceRef = useRef<EventSource | null>(null);
  
  useEffect(() => {
    // Set up event source for server-sent events
    const eventSource = new EventSource(`/api/v1/analysis/stream/${analysisId}`);
    eventSourceRef.current = eventSource;
    
    eventSource.onopen = () => {
      setStatus("connected");
      setLogs(prev => [...prev, "Connected to analysis stream"]);
    };
    
    eventSource.addEventListener("status", (event) => {
      const data = JSON.parse(event.data);
      setStatus(data.status);
      setLogs(prev => [...prev, `Status updated: ${data.status}`]);
    });
    
    eventSource.addEventListener("result", (event) => {
      const data = JSON.parse(event.data);
      setResults(data);
      setLogs(prev => [...prev, "Received analysis results"]);
      
      if (onComplete) {
        onComplete(data);
      }
    });
    
    eventSource.addEventListener("error", (event) => {
      const data = JSON.parse(event.data || '{"error": "Unknown error"}');
      setError(data.error);
      setLogs(prev => [...prev, `Error: ${data.error}`]);
      eventSource.close();
    });
    
    eventSource.addEventListener("done", () => {
      setLogs(prev => [...prev, "Analysis completed"]);
      eventSource.close();
    });
    
    // Clean up
    return () => {
      eventSource.close();
    };
  }, [analysisId, onComplete]);
  
  // Auto-scroll logs
  const logsEndRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs]);
  
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">Analysis Progress</h3>
        <StatusBadge status={status as Analysis["status"]} />
      </div>
      
      <Card>
        <CardContent className="p-4">
          <div className="bg-muted/50 rounded-md p-4 h-80 overflow-y-auto font-mono text-sm">
            {logs.length === 0 ? (
              <div className="text-muted-foreground">Waiting for analysis to start...</div>
            ) : (
              <>
                {logs.map((log, index) => (
                  <div key={index} className="mb-2">
                    <span className="text-muted-foreground">[{new Date().toLocaleTimeString()}]</span> {log}
                  </div>
                ))}
                <div ref={logsEndRef} />
              </>
            )}
          </div>
        </CardContent>
      </Card>
      
      {error && (
        <div className="bg-destructive/10 border border-destructive/50 text-destructive rounded-md p-4">
          {error}
        </div>
      )}
    </div>
  );
}
