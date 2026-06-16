"use client";

import { motion } from "framer-motion";
import {
  AlertTriangle,
  MapPin,
  Fingerprint,
  Lightbulb,
  Target,
} from "lucide-react";
import type { ProfileSummary } from "@/lib/types";
import { formatConfidence } from "@/lib/utils";

interface ProfileSummaryProps {
  profile: ProfileSummary;
}

export function ProfileSummaryCard({ profile }: ProfileSummaryProps) {
  const assessment = profile.confidence_assessment;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card border-accent/30 bg-gradient-to-br from-bg-secondary to-accent-dim"
    >
      <div className="flex items-center gap-2 mb-4">
        <Target className="w-5 h-5 text-accent" />
        <h3 className="font-display text-lg font-bold text-text-primary">
          AI Profil Özeti
        </h3>
      </div>

      {profile.identity_summary && (
        <p className="text-text-primary leading-relaxed mb-4">
          {profile.identity_summary}
        </p>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        {profile.estimated_location && (
          <div className="flex items-start gap-2">
            <MapPin className="w-4 h-4 text-accent mt-0.5 shrink-0" />
            <div>
              <p className="text-xs text-text-secondary uppercase">Konum</p>
              <p className="text-sm text-text-primary">
                {profile.estimated_location}
              </p>
            </div>
          </div>
        )}
        {profile.digital_footprint && (
          <div className="flex items-start gap-2">
            <Fingerprint className="w-4 h-4 text-accent mt-0.5 shrink-0" />
            <div>
              <p className="text-xs text-text-secondary uppercase">
                Dijital Ayak İzi
              </p>
              <p className="text-sm text-text-primary">
                {profile.digital_footprint}
              </p>
            </div>
          </div>
        )}
      </div>

      {assessment && (
        <div className="grid grid-cols-4 gap-2 mb-4">
          {Object.entries(assessment).map(([key, val]) => (
            <div key={key} className="bg-bg-tertiary rounded-lg p-2 text-center">
              <p className="text-xs text-text-secondary capitalize">
                {key.replace("_", " ")}
              </p>
              <p className="font-mono text-accent font-bold">
                {formatConfidence(val)}
              </p>
            </div>
          ))}
        </div>
      )}

      {profile.key_findings && profile.key_findings.length > 0 && (
        <div className="mb-4">
          <p className="text-xs text-text-secondary uppercase mb-2">
            Önemli Bulgular
          </p>
          <ul className="space-y-1">
            {profile.key_findings.map((f, i) => (
              <li key={i} className="text-sm text-text-primary flex items-start gap-2">
                <span className="text-accent mt-1">•</span>
                {f}
              </li>
            ))}
          </ul>
        </div>
      )}

      {profile.recommended_next_steps &&
        profile.recommended_next_steps.length > 0 && (
          <div className="mb-4">
            <div className="flex items-center gap-1 mb-2">
              <Lightbulb className="w-4 h-4 text-warning" />
              <p className="text-xs text-text-secondary uppercase">
                Önerilen Adımlar
              </p>
            </div>
            <ul className="space-y-1">
              {profile.recommended_next_steps.map((s, i) => (
                <li key={i} className="text-sm text-text-secondary">
                  {i + 1}. {s}
                </li>
              ))}
            </ul>
          </div>
        )}

      {profile.risk_flags && profile.risk_flags.length > 0 && (
        <div className="bg-danger/10 border border-danger/30 rounded-lg p-3">
          <div className="flex items-center gap-1 mb-2">
            <AlertTriangle className="w-4 h-4 text-danger" />
            <p className="text-sm font-medium text-danger">Risk İşaretleri</p>
          </div>
          <ul className="space-y-1">
            {profile.risk_flags.map((r, i) => (
              <li key={i} className="text-sm text-danger/80">
                {r}
              </li>
            ))}
          </ul>
        </div>
      )}
    </motion.div>
  );
}
