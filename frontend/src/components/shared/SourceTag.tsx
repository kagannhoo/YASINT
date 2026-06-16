interface SourceTagProps {
  source: string;
}

export function SourceTag({ source }: SourceTagProps) {
  return (
    <span className="inline-flex items-center gap-1 text-xs font-mono bg-bg-tertiary text-text-secondary px-2 py-0.5 rounded border border-border">
      {source}
    </span>
  );
}
