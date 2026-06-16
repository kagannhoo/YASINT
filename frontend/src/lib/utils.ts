import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("tr-TR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatConfidence(score: number): string {
  return `${Math.round(score * 100)}%`;
}

export function parseFindingValue(
  value: string | number | Record<string, unknown>
): string {
  if (typeof value === "object") {
    return JSON.stringify(value, null, 2);
  }
  return String(value);
}
