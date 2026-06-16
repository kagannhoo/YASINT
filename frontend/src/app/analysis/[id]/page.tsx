"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { motion } from "framer-motion";
import {
  Download,
  FileJson,
  Share2,
  ExternalLink,
} from "lucide-react";
import { TopBar } from "@/components/layout/TopBar";
import { ModuleStatus } from "@/components/analysis/ModuleStatus";
import { ResultCard } from "@/components/analysis/ResultCard";
import { MapView } from "@/components/analysis/MapView";
import { TimelineView } from "@/components/analysis/TimelineView";
import { NetworkGraph } from "@/components/analysis/NetworkGraph";
import { FacePanel } from "@/components/analysis/FacePanel";
import { ProfileSummaryCard } from "@/components/analysis/ProfileSummary";
import { DiscoveredIntel } from "@/components/analysis/DiscoveredIntel";
import { IdentityDossier } from "@/components/analysis/IdentityDossier";
import { ConfidenceScore } from "@/components/analysis/ConfidenceScore";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useAnalysisModules, modulesFromTargets } from "@/hooks/useAnalysis";
import {
  getAnalysis,
  getPdfUrl,
  getJsonExportUrl,
} from "@/lib/api";
import type {
  Analysis,
  Finding,
  ModuleName,
  ProfileSummary,
  WSMessage,
} from "@/lib/types";
import { cn, formatConfidence } from "@/lib/utils";

const TABS = [
  { id: "overview", label: "Genel Bakış" },
  { id: "location", label: "Konum" },
  { id: "identity", label: "Kimlik" },
  { id: "social", label: "Sosyal" },
  { id: "network", label: "Ağ" },
  { id: "timeline", label: "Zaman Çizelgesi" },
] as const;

type TabId = (typeof TABS)[number]["id"];

function parseProfile(findings: Finding[]): ProfileSummary | null {
  const llm = findings.find(
    (f) => f.module === "llm" && f.key === "profile_summary"
  );
  if (!llm) return null;
  try {
    return typeof llm.value === "string"
      ? JSON.parse(llm.value)
      : (llm.value as ProfileSummary);
  } catch {
    return null;
  }
}

export default function AnalysisResultPage() {
  const params = useParams();
  const analysisId = params.id as string;

  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [activeTab, setActiveTab] = useState<TabId>("overview");
  const [copied, setCopied] = useState(false);
  const [wsError, setWsError] = useState<string | null>(null);

  const {
    modules,
    findings,
    confidence,
    isComplete,
    initModules,
    handleModuleUpdate,
    setFindings,
    setConfidence,
  } = useAnalysisModules();

  const [stuckWarning, setStuckWarning] = useState(false);

  const loadAnalysis = useCallback(async () => {
    try {
      const data = await getAnalysis(analysisId);
      setAnalysis(data);
      initModules(modulesFromTargets(data.targets));
      if (data.findings && data.findings.length > 0) {
        setFindings(data.findings);
        setConfidence(data.confidence_score);
      }
      if (data.status === "completed") {
        handleModuleUpdate("system", "completed", []);
      }
    } catch {
      // API may not be running yet
    }
  }, [analysisId, initModules, setFindings, setConfidence, handleModuleUpdate]);

  useEffect(() => {
    loadAnalysis();
  }, [analysisId, loadAnalysis]);

  // Celery gecikirse API'den periyodik yenile
  useEffect(() => {
    if (isComplete || analysis?.status === "completed" || analysis?.status === "failed") {
      return;
    }
    const interval = setInterval(loadAnalysis, 5000);
    const stuckTimer = setTimeout(() => setStuckWarning(true), 90000);
    return () => {
      clearInterval(interval);
      clearTimeout(stuckTimer);
    };
  }, [isComplete, analysis?.status, loadAnalysis]);

  const onWSMessage = useCallback(
    (msg: WSMessage) => {
      if (msg.event === "connected") return;

      if (msg.module) {
        const status =
          msg.event === "module_error"
            ? "failed"
            : msg.status === "running"
            ? "running"
            : "completed";

        const newFindings: Finding[] = (msg.findings || []).map((f) => ({
          module: f.module || msg.module || "",
          category: f.category || "",
          key: f.key || "",
          value: f.value ?? "",
          confidence: f.confidence,
          source: f.source,
          raw_data: f.raw_data,
        }));

        handleModuleUpdate(msg.module, status, newFindings, msg.error);
      }

      if (msg.module === "system" && msg.status === "completed") {
        loadAnalysis();
      }
    },
    [handleModuleUpdate, setFindings, loadAnalysis]
  );

  const { connected, error: wsConnError } = useWebSocket(
    analysisId,
    onWSMessage
  );

  useEffect(() => {
    setWsError(wsConnError);
  }, [wsConnError]);

  const profile = parseProfile(findings);
  const locations = analysis?.locations || [];

  const filterFindings = (category: string) =>
    findings.filter((f) => f.category === category && f.module !== "llm");

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div>
      <TopBar
        title={analysis?.target_name || "Analiz Sonuçları"}
        subtitle={
          connected
            ? "Canlı güncelleme aktif"
            : wsError || "Bağlantı bekleniyor..."
        }
      />

      {stuckWarning && analysis?.status === "pending" && (
        <div className="mb-4 bg-warning/10 border border-warning/30 text-warning text-sm rounded-lg p-3">
          Analiz beklenenden uzun sürüyor. Celery worker yeniden başlatılıyor olabilir —
          sayfayı yenileyin veya yeni analiz başlatın.
        </div>
      )}

      {analysis?.status === "running" && (
        <p className="mb-4 text-text-secondary text-sm">
          Tahmini süre: fotoğraf + kullanıcı adı + e-posta için 1–3 dakika
          (Sherlock ve DeepFace en uzun adımlardır).
        </p>
      )}

      <section className="mb-8">
        <ModuleStatus modules={modules} />
      </section>

      <section className="mb-8">
        <div className="flex gap-1 border-b border-border mb-6 overflow-x-auto">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "px-4 py-2.5 text-sm font-medium whitespace-nowrap transition-colors border-b-2 -mb-px",
                activeTab === tab.id
                  ? "text-accent border-accent"
                  : "text-text-secondary border-transparent hover:text-text-primary"
              )}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {activeTab === "overview" && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
          >
            {profile && <ProfileSummaryCard profile={profile} />}
            <DiscoveredIntel findings={findings} />
            <IdentityDossier findings={findings} />

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="card flex flex-col items-center justify-center">
                <ConfidenceScore
                  score={confidence || analysis?.confidence_score || 0}
                />
              </div>
              <div className="md:col-span-2 space-y-3">
                <h3 className="font-display font-semibold text-text-primary">
                  Temel Bulgular
                </h3>
                {findings
                  .filter((f) => f.module !== "llm")
                  .slice(0, 5)
                  .map((f, i) => (
                    <ResultCard key={`${f.key}-${i}`} finding={f} />
                  ))}
                {findings.length === 0 && (
                  <p className="text-text-secondary text-sm">
                    {isComplete
                      ? "Bulgu bulunamadı"
                      : "Analiz devam ediyor..."}
                  </p>
                )}
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === "location" && (
          <div className="space-y-4">
            <MapView locations={locations} />
            <div className="card overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-xs uppercase text-text-secondary border-b border-border">
                    <th className="text-left py-2 px-2">Kaynak</th>
                    <th className="text-left py-2 px-2">Koordinat</th>
                    <th className="text-left py-2 px-2">Doğruluk</th>
                    <th className="text-left py-2 px-2">Güven</th>
                  </tr>
                </thead>
                <tbody>
                  {locations.map((loc) => (
                    <tr
                      key={loc.id}
                      className="border-b border-border/50 hover:bg-bg-tertiary"
                    >
                      <td className="py-2 px-2 font-mono text-xs">{loc.source}</td>
                      <td className="py-2 px-2 font-mono text-xs text-accent">
                        {loc.latitude.toFixed(4)}, {loc.longitude.toFixed(4)}
                      </td>
                      <td className="py-2 px-2 text-text-secondary">
                        {loc.accuracy_meters ? `${loc.accuracy_meters}m` : "—"}
                      </td>
                      <td className="py-2 px-2">
                        {loc.confidence
                          ? formatConfidence(loc.confidence)
                          : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === "identity" && (
          <div className="space-y-4">
            <FacePanel findings={findings} />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {filterFindings("identity").map((f, i) => (
                <ResultCard key={`${f.key}-${i}`} finding={f} />
              ))}
            </div>
          </div>
        )}

        {activeTab === "social" && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {filterFindings("social").map((f, i) => (
                <div key={`${f.key}-${i}`} className="card flex items-center justify-between">
                  <ResultCard finding={f} />
                  {typeof f.value === "string" && f.value.startsWith("http") && (
                    <a
                      href={f.value}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-accent ml-2 shrink-0"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                </div>
              ))}
            </div>
            <NetworkGraph
              findings={findings}
              targetName={analysis?.target_name}
            />
          </div>
        )}

        {activeTab === "network" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {filterFindings("network").map((f, i) => (
              <ResultCard key={`${f.key}-${i}`} finding={f} />
            ))}
            {filterFindings("network").length === 0 && (
              <p className="text-text-secondary col-span-2 text-center py-8">
                Ağ verisi bulunamadı
              </p>
            )}
          </div>
        )}

        {activeTab === "timeline" && <TimelineView findings={findings} />}
      </section>

      <section className="card flex flex-wrap gap-3">
        <a
          href={getPdfUrl(analysisId)}
          target="_blank"
          rel="noopener noreferrer"
          className="btn-primary flex items-center gap-2"
        >
          <Download className="w-4 h-4" />
          PDF İndir
        </a>
        <a
          href={getJsonExportUrl(analysisId)}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 px-4 py-2 border border-border rounded-lg text-text-primary hover:bg-bg-tertiary transition-colors"
        >
          <FileJson className="w-4 h-4" />
          JSON Dışa Aktar
        </a>
        <button
          onClick={handleShare}
          className="flex items-center gap-2 px-4 py-2 border border-border rounded-lg text-text-primary hover:bg-bg-tertiary transition-colors"
        >
          <Share2 className="w-4 h-4" />
          {copied ? "Kopyalandı!" : "Paylaş"}
        </button>
      </section>
    </div>
  );
}
