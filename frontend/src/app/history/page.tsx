"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { TopBar } from "@/components/layout/TopBar";
import { getAnalysisHistory } from "@/lib/api";
import type { AnalysisListItem } from "@/lib/types";
import { formatDate, formatConfidence } from "@/lib/utils";

function StatusBadge({ status }: { status: string }) {
  const classes: Record<string, string> = {
    completed: "badge-success",
    running: "badge-warning",
    pending: "badge-gray",
    failed: "badge-danger",
  };
  const labels: Record<string, string> = {
    completed: "Tamamlandı",
    running: "Çalışıyor",
    pending: "Bekliyor",
    failed: "Başarısız",
  };
  return (
    <span className={classes[status] || "badge-gray"}>
      {labels[status] || status}
    </span>
  );
}

export default function HistoryPage() {
  const [analyses, setAnalyses] = useState<AnalysisListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAnalysisHistory(100)
      .then(setAnalyses)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <TopBar
        title="Geçmiş Analizler"
        subtitle="Tüm analiz oturumlarının listesi"
      />

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-text-secondary text-xs uppercase border-b border-border">
              <th className="text-left py-3 px-3">Hedef</th>
              <th className="text-left py-3 px-3">Tarih</th>
              <th className="text-left py-3 px-3">Durum</th>
              <th className="text-left py-3 px-3">Güven Skoru</th>
              <th className="text-right py-3 px-3">İşlem</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={5} className="text-center py-8 text-text-secondary">
                  Yükleniyor...
                </td>
              </tr>
            )}
            {!loading && analyses.length === 0 && (
              <tr>
                <td colSpan={5} className="text-center py-8 text-text-secondary">
                  Henüz analiz yok
                </td>
              </tr>
            )}
            {analyses.map((item, i) => (
              <tr
                key={item.id}
                className={`border-b border-border/50 hover:bg-bg-tertiary transition-colors ${
                  i % 2 === 0 ? "" : "bg-bg-tertiary/30"
                }`}
              >
                <td className="py-3 px-3 text-text-primary font-medium">
                  {item.target_name || "İsimsiz Hedef"}
                </td>
                <td className="py-3 px-3 text-text-secondary font-mono text-xs">
                  {formatDate(item.created_at)}
                </td>
                <td className="py-3 px-3">
                  <StatusBadge status={item.status} />
                </td>
                <td className="py-3 px-3 font-mono text-accent">
                  {formatConfidence(item.confidence_score)}
                </td>
                <td className="py-3 px-3 text-right">
                  <Link
                    href={`/analysis/${item.id}`}
                    className="text-accent hover:underline text-xs"
                  >
                    Görüntüle →
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
