"use client";

import { User, Smile, Calendar } from "lucide-react";
import type { Finding } from "@/lib/types";
import { ConfidenceBadge } from "@/components/shared/ConfidenceBadge";

interface FacePanelProps {
  findings: Finding[];
}

export function FacePanel({ findings }: FacePanelProps) {
  const faceFindings = findings.filter((f) => f.module === "face");

  if (faceFindings.length === 0) {
    return (
      <div className="card text-center text-text-secondary py-8">
        Yüz analizi verisi bulunamadı
      </div>
    );
  }

  const getValue = (key: string) =>
    faceFindings.find((f) => f.key === key);

  const age = getValue("estimated_age");
  const gender = getValue("gender");
  const emotion = getValue("dominant_emotion");

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      {age && (
        <div className="card flex items-center gap-4">
          <div className="p-3 bg-accent-dim rounded-lg">
            <Calendar className="w-6 h-6 text-accent" />
          </div>
          <div>
            <p className="text-text-secondary text-sm">Tahmini Yaş</p>
            <p className="text-2xl font-display font-bold text-text-primary">
              {String(age.value)}
            </p>
            {age.confidence && (
              <ConfidenceBadge confidence={age.confidence} size="sm" />
            )}
          </div>
        </div>
      )}

      {gender && (
        <div className="card flex items-center gap-4">
          <div className="p-3 bg-accent-dim rounded-lg">
            <User className="w-6 h-6 text-accent" />
          </div>
          <div>
            <p className="text-text-secondary text-sm">Cinsiyet</p>
            <p className="text-2xl font-display font-bold text-text-primary capitalize">
              {String(gender.value)}
            </p>
            {gender.confidence && (
              <ConfidenceBadge confidence={gender.confidence} size="sm" />
            )}
          </div>
        </div>
      )}

      {emotion && (
        <div className="card flex items-center gap-4">
          <div className="p-3 bg-accent-dim rounded-lg">
            <Smile className="w-6 h-6 text-accent" />
          </div>
          <div>
            <p className="text-text-secondary text-sm">Baskın Duygu</p>
            <p className="text-2xl font-display font-bold text-text-primary capitalize">
              {String(emotion.value)}
            </p>
            {emotion.confidence && (
              <ConfidenceBadge confidence={emotion.confidence} size="sm" />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
