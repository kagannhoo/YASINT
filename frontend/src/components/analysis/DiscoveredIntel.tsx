"use client";

import { motion } from "framer-motion";
import { Search, User, Sparkles, Link2, Mail, Globe } from "lucide-react";
import type { Finding } from "@/lib/types";

interface DiscoverySummary {
  you_provided?: Record<string, unknown>;
  we_found?: {
    emails?: string[];
    usernames?: string[];
    platform_urls?: string[];
    ips?: string[];
  };
  message?: string;
}

function parseSummary(findings: Finding[]): DiscoverySummary | null {
  const f = findings.find(
    (x) => x.module === "enrich" && x.key === "discovery_summary"
  );
  if (!f) return null;
  try {
    return typeof f.value === "string" ? JSON.parse(f.value) : (f.value as DiscoverySummary);
  } catch {
    return null;
  }
}

export function DiscoveredIntel({ findings }: { findings: Finding[] }) {
  const summary = parseSummary(findings);
  if (!summary) return null;

  const provided = summary.you_provided || {};
  const found = summary.we_found || {};
  const hasFound = Object.values(found).some(
    (v) => Array.isArray(v) && v.length > 0
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="card border-accent/40 mb-6"
    >
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="w-5 h-5 text-accent" />
        <h3 className="font-display font-bold text-text-primary">
          Otomatik Keşif
        </h3>
      </div>

      {summary.message && (
        <p className="text-text-primary mb-4 text-sm leading-relaxed">
          {summary.message}
        </p>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-bg-tertiary rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3 text-text-secondary text-xs uppercase tracking-wider">
            <User className="w-3.5 h-3.5" />
            Sen verdin
          </div>
          <ul className="space-y-1.5">
            {Object.entries(provided).map(([k, v]) => (
              <li key={k} className="text-sm text-text-primary">
                <span className="text-text-secondary capitalize">{k}: </span>
                {k === "photo" ? "1 fotoğraf" : String(v)}
              </li>
            ))}
            {Object.keys(provided).length === 0 && (
              <li className="text-sm text-text-secondary">—</li>
            )}
          </ul>
        </div>

        <div className="bg-accent-dim rounded-lg p-4 border border-accent/20">
          <div className="flex items-center gap-2 mb-3 text-accent text-xs uppercase tracking-wider">
            <Search className="w-3.5 h-3.5" />
            Sistem buldu
          </div>
          {!hasFound ? (
            <p className="text-sm text-text-secondary">
              Ek açık kaynak bulgusu sınırlı — farklı bir ipucu deneyin.
            </p>
          ) : (
            <ul className="space-y-2">
              {found.emails?.map((e) => (
                <li key={e} className="flex items-center gap-2 text-sm text-text-primary">
                  <Mail className="w-3.5 h-3.5 text-accent shrink-0" />
                  {e}
                </li>
              ))}
              {found.platform_urls?.map((u) => (
                <li key={u} className="flex items-center gap-2 text-sm">
                  <Link2 className="w-3.5 h-3.5 text-accent shrink-0" />
                  <a
                    href={u}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-accent hover:underline truncate"
                  >
                    {u.replace("https://", "")}
                  </a>
                </li>
              ))}
              {found.usernames?.map((u) => (
                <li key={u} className="flex items-center gap-2 text-sm text-text-primary">
                  <Globe className="w-3.5 h-3.5 text-accent shrink-0" />@{u}
                </li>
              ))}
              {found.ips?.map((ip) => (
                <li key={ip} className="text-sm font-mono text-text-primary">
                  {ip}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </motion.div>
  );
}
