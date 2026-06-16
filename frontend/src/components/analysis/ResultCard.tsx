"use client";

import { motion } from "framer-motion";
import { ConfidenceBadge } from "@/components/shared/ConfidenceBadge";
import { SourceTag } from "@/components/shared/SourceTag";
import type { Finding } from "@/lib/types";
import { parseFindingValue } from "@/lib/utils";

interface ResultCardProps {
  finding: Finding;
  highlight?: boolean;
}

export function ResultCard({ finding, highlight }: ResultCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className={`card ${highlight ? "border-accent/50 bg-accent-dim" : ""}`}
    >
      <div className="flex items-start justify-between gap-3 mb-2">
        <div>
          <span className="text-xs uppercase tracking-wider text-text-secondary">
            {finding.category}
          </span>
          <h4 className="font-medium text-text-primary mt-0.5">
            {finding.key.replace(/_/g, " ")}
          </h4>
        </div>
        {finding.confidence !== undefined && (
          <ConfidenceBadge confidence={finding.confidence} size="sm" />
        )}
      </div>
      <pre className="text-sm text-text-primary font-mono whitespace-pre-wrap break-all bg-bg-tertiary rounded p-2 max-h-32 overflow-auto">
        {parseFindingValue(finding.value)}
      </pre>
      {finding.source && (
        <div className="mt-2">
          <SourceTag source={finding.source} />
        </div>
      )}
    </motion.div>
  );
}
