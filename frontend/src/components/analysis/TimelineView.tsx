"use client";

import { motion } from "framer-motion";
import type { Finding } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import { SourceTag } from "@/components/shared/SourceTag";

interface TimelineViewProps {
  findings: Finding[];
}

export function TimelineView({ findings }: TimelineViewProps) {
  const timelineItems = findings
    .filter((f) => f.category === "timeline" || f.key.includes("time"))
    .sort((a, b) => {
      const dateA = new Date(String(a.value)).getTime() || 0;
      const dateB = new Date(String(b.value)).getTime() || 0;
      return dateB - dateA;
    });

  if (timelineItems.length === 0) {
    return (
      <div className="card text-center text-text-secondary py-8">
        Zaman çizelgesi verisi bulunamadı
      </div>
    );
  }

  return (
    <div className="space-y-0">
      {timelineItems.map((item, i) => (
        <motion.div
          key={`${item.key}-${i}`}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.1 }}
          className="flex gap-4"
        >
          <div className="flex flex-col items-center">
            <div className="w-3 h-3 rounded-full bg-accent mt-1.5" />
            {i < timelineItems.length - 1 && (
              <div className="w-px flex-1 bg-border my-1" />
            )}
          </div>
          <div className="card flex-1 mb-4">
            <div className="flex items-center justify-between mb-1">
              <span className="font-mono text-sm text-accent">
                {String(item.value)}
              </span>
              {item.created_at && (
                <span className="text-xs text-text-secondary">
                  {formatDate(item.created_at)}
                </span>
              )}
            </div>
            <p className="text-sm text-text-primary">
              {item.key.replace(/_/g, " ")} — {item.module} modülü
            </p>
            {item.source && (
              <div className="mt-2">
                <SourceTag source={item.source} />
              </div>
            )}
          </div>
        </motion.div>
      ))}
    </div>
  );
}
