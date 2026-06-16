"use client";

import { motion } from "framer-motion";
import {
  Camera,
  User,
  MapPin,
  AtSign,
  Globe,
  Mail,
  Brain,
  Loader2,
  CheckCircle2,
  XCircle,
  Clock,
  Sparkles,
} from "lucide-react";
import type { ModuleState } from "@/lib/types";
import { cn } from "@/lib/utils";

const MODULE_ICONS: Record<string, React.ElementType> = {
  exif: Camera,
  face: User,
  geo: MapPin,
  reverse_image: Camera,
  username: AtSign,
  social: Globe,
  ip: Globe,
  email: Mail,
  enrich: Sparkles,
  llm: Brain,
};

const STATUS_CONFIG = {
  pending: { icon: Clock, color: "text-text-secondary", label: "Bekleniyor" },
  running: { icon: Loader2, color: "text-accent", label: "Çalışıyor" },
  completed: { icon: CheckCircle2, color: "text-success", label: "Tamamlandı" },
  failed: { icon: XCircle, color: "text-danger", label: "Hata" },
};

interface ModuleStatusProps {
  modules: ModuleState[];
}

export function ModuleStatus({ modules }: ModuleStatusProps) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-8 gap-3">
      {modules.map((mod, i) => {
        const Icon = MODULE_ICONS[mod.name] || Globe;
        const status = STATUS_CONFIG[mod.status];
        const StatusIcon = status.icon;

        return (
          <motion.div
            key={mod.name}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className={cn(
              "card relative overflow-hidden",
              mod.status === "running" && "border-accent/50"
            )}
          >
            {mod.status === "running" && (
              <div className="absolute left-0 top-0 bottom-0 w-1 bg-accent animate-pulse" />
            )}
            <div className="flex items-center gap-2 mb-2">
              <Icon className="w-4 h-4 text-accent" />
              <span className="text-xs font-medium text-text-primary truncate">
                {mod.label}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className={cn("flex items-center gap-1", status.color)}>
                <StatusIcon
                  className={cn(
                    "w-3.5 h-3.5",
                    mod.status === "running" && "animate-spin"
                  )}
                />
                <span className="text-xs">{status.label}</span>
              </div>
              {mod.findingsCount > 0 && (
                <span className="text-xs font-mono text-accent">
                  {mod.findingsCount}
                </span>
              )}
            </div>
            {mod.error && (
              <p className="text-xs text-danger mt-1 truncate" title={mod.error}>
                {mod.error}
              </p>
            )}
          </motion.div>
        );
      })}
    </div>
  );
}
