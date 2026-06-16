"use client";

import { useCallback, useState } from "react";
import type { Finding, ModuleName, ModuleState } from "@/lib/types";

const DEFAULT_MODULES: ModuleState[] = [
  { name: "exif", label: "EXIF Analizi", status: "pending", findingsCount: 0 },
  { name: "face", label: "Yüz Analizi", status: "pending", findingsCount: 0 },
  { name: "geo", label: "Konum Tahmini", status: "pending", findingsCount: 0 },
  { name: "reverse_image", label: "Ters Görüntü", status: "pending", findingsCount: 0 },
  { name: "username", label: "Kullanıcı Adı", status: "pending", findingsCount: 0 },
  { name: "social", label: "Sosyal Medya", status: "pending", findingsCount: 0 },
  { name: "ip", label: "IP Analizi", status: "pending", findingsCount: 0 },
  { name: "phone", label: "Telefon OSINT", status: "pending", findingsCount: 0 },
  { name: "email", label: "E-posta", status: "pending", findingsCount: 0 },
  { name: "email_reg", label: "Kayıt Tespiti", status: "pending", findingsCount: 0 },
  { name: "breach", label: "Veri İhlali", status: "pending", findingsCount: 0 },
  { name: "domain", label: "Domain Intel", status: "pending", findingsCount: 0 },
  { name: "paste", label: "Paste/Kod", status: "pending", findingsCount: 0 },
  { name: "dork", label: "Web Dork", status: "pending", findingsCount: 0 },
  { name: "enrich", label: "Otomatik Keşif", status: "pending", findingsCount: 0 },
  { name: "dossier", label: "Kimlik Dosyası", status: "pending", findingsCount: 0 },
  { name: "llm", label: "AI Profil", status: "pending", findingsCount: 0 },
];

export function modulesFromTargets(
  targets?: Array<{ data_type: string }>
): ModuleName[] {
  const active = new Set<ModuleName>(["llm", "enrich", "dossier"]);
  if (!targets) return Array.from(active);

  for (const t of targets) {
    switch (t.data_type) {
      case "image":
        active.add("exif");
        active.add("face");
        active.add("geo");
        active.add("reverse_image");
        break;
      case "username":
        active.add("username");
        active.add("social");
        active.add("paste");
        active.add("dork");
        break;
      case "ip":
        active.add("ip");
        break;
      case "phone":
        active.add("phone");
        break;
      case "email":
        active.add("email");
        active.add("email_reg");
        active.add("breach");
        active.add("domain");
        active.add("paste");
        active.add("dork");
        break;
      case "url":
        active.add("social");
        break;
    }
  }
  return Array.from(active);
}

export function useAnalysisModules(activeModules?: ModuleName[]) {
  const [modules, setModules] = useState<ModuleState[]>(DEFAULT_MODULES);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [confidence, setConfidence] = useState(0);
  const [isComplete, setIsComplete] = useState(false);

  const initModules = useCallback((active: ModuleName[]) => {
    setModules(
      DEFAULT_MODULES.filter((m) => active.includes(m.name)).map((m) => ({
        ...m,
        status: "pending" as const,
      }))
    );
  }, []);

  const handleModuleUpdate = useCallback(
    (
      moduleName: string,
      status: ModuleState["status"],
      newFindings: Finding[],
      error?: string
    ) => {
      setModules((prev) =>
        prev.map((m) =>
          m.name === moduleName
            ? {
                ...m,
                status,
                findingsCount:
                  newFindings.length > 0 ? newFindings.length : m.findingsCount,
                error,
              }
            : m
        )
      );

      if (newFindings.length > 0) {
        setFindings((prev) => {
          const merged = [...prev, ...newFindings];
          const scores = merged
            .map((f) => f.confidence ?? 0)
            .filter((c) => c > 0);
          if (scores.length > 0) {
            setConfidence(scores.reduce((a, b) => a + b, 0) / scores.length);
          }
          return merged;
        });
      }

      if (moduleName === "system" && status === "completed") {
        setIsComplete(true);
      }
    },
    []
  );

  return {
    modules,
    findings,
    confidence,
    isComplete,
    initModules,
    handleModuleUpdate,
    setFindings,
    setConfidence,
  };
}
