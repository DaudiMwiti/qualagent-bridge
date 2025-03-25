
import { AgentPreset } from "@/types/agent-presets";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Check, AlertCircle, Beaker, BookOpen, BrainCircuit } from "lucide-react";
import { cn } from "@/lib/utils";

interface AgentPresetSelectorProps {
  presets: AgentPreset[];
  selectedPresetId: string | null;
  onSelectPreset: (preset: AgentPreset) => void;
  isLoading?: boolean;
}

export function AgentPresetSelector({
  presets,
  selectedPresetId,
  onSelectPreset,
  isLoading = false,
}: AgentPresetSelectorProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-2">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="border border-border/30 bg-card/30 h-[200px] animate-pulse">
            <CardHeader className="h-1/2 bg-muted/20 rounded-t-lg"></CardHeader>
            <CardContent className="h-1/4 mt-2">
              <div className="h-4 w-3/4 bg-muted/20 rounded"></div>
              <div className="h-4 w-1/2 bg-muted/20 rounded mt-2"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (!presets?.length) {
    return (
      <div className="border border-yellow-500/30 bg-yellow-500/10 text-yellow-600 rounded-lg p-4 flex gap-2 items-center">
        <AlertCircle size={20} />
        <p>No agent presets available. Please try again later or contact support.</p>
      </div>
    );
  }

  // Map of preset complexity to appropriate icon
  const complexityIcons = {
    basic: BookOpen,
    intermediate: Beaker,
    advanced: BrainCircuit,
  };

  // Function to get complexity label and color
  const getComplexityProps = (complexity?: string) => {
    switch (complexity) {
      case "basic":
        return { label: "Basic", color: "bg-blue-500" };
      case "intermediate":
        return { label: "Intermediate", color: "bg-purple-500" };
      case "advanced":
        return { label: "Advanced", color: "bg-orange-500" };
      default:
        return { label: "Standard", color: "bg-gray-500" };
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-2">
      {presets.map((preset) => {
        const isSelected = selectedPresetId === preset.id;
        const ComplexityIcon = preset.complexity ? complexityIcons[preset.complexity] : BookOpen;
        const complexityProps = getComplexityProps(preset.complexity);

        return (
          <Card
            key={preset.id}
            className={cn(
              "border-2 cursor-pointer transition-all hover:shadow-md relative overflow-hidden",
              isSelected ? "border-primary" : "border-transparent"
            )}
            onClick={() => onSelectPreset(preset)}
          >
            {isSelected && (
              <div className="absolute top-0 right-0 bg-primary text-primary-foreground p-1 rounded-bl-md">
                <Check size={16} />
              </div>
            )}
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle className="text-lg">{preset.name}</CardTitle>
                <Badge variant="outline" className={`${complexityProps.color} text-white`}>
                  <ComplexityIcon size={14} className="mr-1" />
                  {complexityProps.label}
                </Badge>
              </div>
              <CardDescription>{preset.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-1">
                {preset.tools.map((tool) => (
                  <Badge key={tool} variant="secondary" className="text-xs">
                    {tool}
                  </Badge>
                ))}
              </div>
            </CardContent>
            {preset.suitableFor && (
              <CardFooter className="pt-0 text-sm text-muted-foreground border-t border-border/50 mt-2">
                <strong className="mr-1">Best for:</strong> {preset.suitableFor}
              </CardFooter>
            )}
          </Card>
        );
      })}
    </div>
  );
}
