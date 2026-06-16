import { cn, formatConfidence } from "@/lib/utils";

interface ConfidenceBadgeProps {
  confidence: number;
  size?: "sm" | "md" | "lg";
}

export function ConfidenceBadge({
  confidence,
  size = "md",
}: ConfidenceBadgeProps) {
  const pct = confidence * 100;
  const variant =
    pct >= 80 ? "success" : pct >= 50 ? "warning" : "danger";

  const sizeClasses = {
    sm: "text-xs px-1.5 py-0.5",
    md: "text-sm px-2 py-1",
    lg: "text-base px-3 py-1.5",
  };

  return (
    <span
      className={cn(
        "rounded font-medium font-mono",
        sizeClasses[size],
        variant === "success" && "badge-success",
        variant === "warning" && "badge-warning",
        variant === "danger" && "badge-danger"
      )}
    >
      {formatConfidence(confidence)}
    </span>
  );
}
