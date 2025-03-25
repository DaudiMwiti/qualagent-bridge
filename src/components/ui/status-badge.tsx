
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

type AnalysisStatus = "pending" | "in_progress" | "completed" | "failed";

interface StatusBadgeProps {
  status: AnalysisStatus;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const statusConfig = {
    pending: {
      variant: "outline" as const,
      label: "Pending",
      className: "text-yellow-600 border-yellow-400 bg-yellow-50 dark:bg-yellow-950/30",
    },
    in_progress: {
      variant: "outline" as const,
      label: "In Progress",
      className: "text-blue-600 border-blue-400 bg-blue-50 dark:bg-blue-950/30",
    },
    completed: {
      variant: "outline" as const,
      label: "Completed",
      className: "text-green-600 border-green-400 bg-green-50 dark:bg-green-950/30",
    },
    failed: {
      variant: "outline" as const,
      label: "Failed",
      className: "text-red-600 border-red-400 bg-red-50 dark:bg-red-950/30",
    },
  };

  const config = statusConfig[status];

  return (
    <Badge
      variant={config.variant}
      className={cn(config.className, className)}
    >
      {config.label}
    </Badge>
  );
}
