"use client";

import { useEffect, useState } from "react";
import { motion, useSpring, useTransform } from "framer-motion";
import { formatConfidence } from "@/lib/utils";

interface ConfidenceScoreProps {
  score: number;
  size?: number;
}

export function ConfidenceScore({ score, size = 120 }: ConfidenceScoreProps) {
  const [displayScore, setDisplayScore] = useState(0);
  const spring = useSpring(0, { stiffness: 50, damping: 20 });
  const display = useTransform(spring, (v) => Math.round(v * 100));

  useEffect(() => {
    spring.set(score);
    const unsub = display.on("change", (v) => setDisplayScore(v));
    return unsub;
  }, [score, spring, display]);

  const radius = (size - 12) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - score * circumference;

  const color =
    score >= 0.8 ? "#10b981" : score >= 0.5 ? "#f59e0b" : "#ef4444";

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#2a2d35"
            strokeWidth="8"
          />
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1, ease: "easeOut" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-display text-2xl font-bold text-text-primary">
            {displayScore}%
          </span>
          <span className="text-xs text-text-secondary">Güven</span>
        </div>
      </div>
    </div>
  );
}
