"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Plus, ArrowRight, BarChart3, Calendar, Target } from "lucide-react";
import { TopBar } from "@/components/layout/TopBar";
import { getDashboardStats, getAnalysisHistory } from "@/lib/api";
import type { AnalysisListItem, DashboardStats } from "@/lib/types";
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

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recent, setRecent] = useState<AnalysisListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getDashboardStats(), getAnalysisHistory(5)])
      .then(([s, h]) => {
        setStats(s);
        setRecent(h);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const metrics = [
    {
      label: "Toplam Analiz",
      value: stats?.total_analyses ?? 0,
      icon: BarChart3,
    },
    {
      label: "Bu Ay",
      value: stats?.this_month ?? 0,
      icon: Calendar,
    },
    {
      label: "Ort. Güven Skoru",
      value: stats ? formatConfidence(stats.avg_confidence) : "—",
      icon: Target,
    },
  ];

  return (
    <div>
      <TopBar
        title="Dashboard"
        subtitle="YASINT analiz özeti ve hızlı erişim"
        actions={
          <Link href="/analysis/new" className="btn-primary flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Yeni Analiz
          </Link>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {metrics.map((m, i) => (
          <motion.div
            key={m.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="card flex items-center gap-4"
          >
            <div className="p-3 bg-accent-dim rounded-lg">
              <m.icon className="w-6 h-6 text-accent" />
            </div>
            <div>
              <p className="text-text-secondary text-sm">{m.label}</p>
              <p className="font-display text-2xl font-bold text-text-primary">
                {loading ? "..." : m.value}
              </p>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-display font-semibold text-text-primary">
            Son Analizler
          </h2>
          <Link
            href="/history"
            className="text-sm text-accent hover:underline flex items-center gap-1"
          >
            Tümünü Gör <ArrowRight className="w-3 h-3" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-text-secondary text-xs uppercase border-b border-border">
                <th className="text-left py-3 px-2">Hedef</th>
                <th className="text-left py-3 px-2">Tarih</th>
                <th className="text-left py-3 px-2">Durum</th>
                <th className="text-left py-3 px-2">Güven</th>
                <th className="text-right py-3 px-2"></th>
              </tr>
            </thead>
            <tbody>
              {recent.length === 0 && !loading && (
                <tr>
                  <td colSpan={5} className="text-center py-8 text-text-secondary">
                    Henüz analiz yok. İlk analizi başlatın.
                  </td>
                </tr>
              )}
              {recent.map((item, i) => (
                <tr
                  key={item.id}
                  className={`border-b border-border/50 hover:bg-bg-tertiary transition-colors ${
                    i % 2 === 0 ? "" : "bg-bg-tertiary/30"
                  }`}
                >
                  <td className="py-3 px-2 text-text-primary">
                    {item.target_name || "İsimsiz"}
                  </td>
                  <td className="py-3 px-2 text-text-secondary font-mono text-xs">
                    {formatDate(item.created_at)}
                  </td>
                  <td className="py-3 px-2">
                    <StatusBadge status={item.status} />
                  </td>
                  <td className="py-3 px-2 font-mono text-accent">
                    {formatConfidence(item.confidence_score)}
                  </td>
                  <td className="py-3 px-2 text-right">
                    <Link
                      href={`/analysis/${item.id}`}
                      className="text-accent hover:underline text-xs"
                    >
                      Sonuç →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
