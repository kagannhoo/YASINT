"use client";

import { motion } from "framer-motion";
import {
  Shield,
  Mail,
  User,
  Globe,
  AlertTriangle,
  Link2,
  Fingerprint,
} from "lucide-react";
import type { Finding } from "@/lib/types";

interface Dossier {
  summary?: string;
  exposure_score?: number;
  identity?: {
    names?: string[];
    emails?: string[];
    usernames?: string[];
  };
  digital_footprint?: {
    social_profiles?: Array<{ platform: string; url: string }>;
    registered_services?: string[];
    web_mentions?: string[];
    profile_photos?: string[];
  };
  security?: {
    breaches?: Array<{ name: string; date: string; data_classes?: string[] }>;
    risk_factors?: string[];
  };
  stats?: Record<string, number>;
}

function parseDossier(findings: Finding[]): Dossier | null {
  const f = findings.find((x) => x.module === "dossier" && x.key === "identity_dossier");
  if (!f) return null;
  try {
    return typeof f.value === "string" ? JSON.parse(f.value) : (f.value as Dossier);
  } catch {
    return null;
  }
}

export function IdentityDossier({ findings }: { findings: Finding[] }) {
  const dossier = parseDossier(findings);
  if (!dossier) return null;

  const exposure = dossier.exposure_score ?? 0;
  const exposureColor =
    exposure >= 0.7 ? "text-danger" : exposure >= 0.4 ? "text-warning" : "text-success";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="card border-2 border-accent/30 mb-6"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-2">
          <Fingerprint className="w-6 h-6 text-accent" />
          <div>
            <h3 className="font-display font-bold text-lg text-text-primary">
              Kimlik Dosyası
            </h3>
            <p className="text-text-secondary text-sm">{dossier.summary}</p>
          </div>
        </div>
        <div className="text-center">
          <p className={`font-display text-3xl font-bold ${exposureColor}`}>
            {Math.round(exposure * 100)}%
          </p>
          <p className="text-xs text-text-secondary">Maruziyet</p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        {[
          { label: "Sosyal Profil", val: dossier.stats?.social_count ?? 0 },
          { label: "E-posta", val: dossier.stats?.email_count ?? 0 },
          { label: "İhlal", val: dossier.stats?.breach_count ?? 0 },
          { label: "Toplam Bulgu", val: dossier.stats?.total_findings ?? 0 },
        ].map((s) => (
          <div key={s.label} className="bg-bg-tertiary rounded-lg p-3 text-center">
            <p className="text-xl font-bold text-accent">{s.val}</p>
            <p className="text-xs text-text-secondary">{s.label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {dossier.identity?.names && dossier.identity.names.length > 0 && (
          <Section icon={User} title="İsimler" items={dossier.identity.names} />
        )}
        {dossier.identity?.emails && dossier.identity.emails.length > 0 && (
          <Section icon={Mail} title="E-postalar" items={dossier.identity.emails} mono />
        )}
        {dossier.digital_footprint?.registered_services &&
          dossier.digital_footprint.registered_services.length > 0 && (
            <Section
              icon={Globe}
              title="Kayıtlı Servisler"
              items={dossier.digital_footprint.registered_services}
            />
          )}
        {dossier.digital_footprint?.social_profiles &&
          dossier.digital_footprint.social_profiles.length > 0 && (
            <div className="bg-bg-tertiary rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2 text-xs uppercase text-text-secondary">
                <Link2 className="w-3.5 h-3.5" />
                Sosyal Profiller
              </div>
              <ul className="space-y-1 max-h-40 overflow-auto">
                {dossier.digital_footprint.social_profiles.map((p, i) => (
                  <li key={i}>
                    <a
                      href={p.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-accent hover:underline truncate block"
                    >
                      {p.platform}: {p.url.replace("https://", "")}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
      </div>

      {dossier.security?.risk_factors && dossier.security.risk_factors.length > 0 && (
        <div className="mt-4 bg-danger/10 border border-danger/30 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-danger" />
            <p className="text-sm font-medium text-danger">Risk Faktörleri</p>
          </div>
          <ul className="space-y-1">
            {dossier.security.risk_factors.map((r, i) => (
              <li key={i} className="text-sm text-danger/80 flex items-center gap-2">
                <Shield className="w-3 h-3 shrink-0" />
                {r}
              </li>
            ))}
          </ul>
        </div>
      )}
    </motion.div>
  );
}

function Section({
  icon: Icon,
  title,
  items,
  mono,
}: {
  icon: React.ElementType;
  title: string;
  items: string[];
  mono?: boolean;
}) {
  return (
    <div className="bg-bg-tertiary rounded-lg p-4">
      <div className="flex items-center gap-2 mb-2 text-xs uppercase text-text-secondary">
        <Icon className="w-3.5 h-3.5" />
        {title}
      </div>
      <ul className="space-y-1">
        {items.map((item, i) => (
          <li
            key={i}
            className={`text-sm text-text-primary ${mono ? "font-mono" : ""}`}
          >
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
