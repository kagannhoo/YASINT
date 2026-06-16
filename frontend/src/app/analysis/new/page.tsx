"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Camera,
  User,
  MapPin,
  AtSign,
  Globe,
  Mail,
  Brain,
  Image as ImageIcon,
  Sparkles,
} from "lucide-react";
import { TopBar } from "@/components/layout/TopBar";
import { InputPanel } from "@/components/analysis/InputPanel";
import type { ModuleName } from "@/lib/types";

const MODULE_INFO: Record<
  ModuleName,
  { label: string; icon: React.ElementType; description: string }
> = {
  exif: {
    label: "EXIF Analizi",
    icon: Camera,
    description: "Fotoğraf metadata, GPS, cihaz bilgisi",
  },
  face: {
    label: "Yüz Analizi",
    icon: User,
    description: "Yaş, cinsiyet, duygu tahmini",
  },
  geo: {
    label: "Konum Tahmini",
    icon: MapPin,
    description: "Görsel içerik analizi",
  },
  reverse_image: {
    label: "Ters Görüntü",
    icon: ImageIcon,
    description: "Görüntü parmak izi ve arama",
  },
  username: {
    label: "Kullanıcı Adı",
    icon: AtSign,
    description: "Sherlock platform taraması",
  },
  social: {
    label: "Sosyal Medya",
    icon: Globe,
    description: "Profil kazıma ve metadata",
  },
  ip: {
    label: "IP Analizi",
    icon: Globe,
    description: "GeoIP, WHOIS, Nmap port taraması (açık kaynak)",
  },
  email: {
    label: "E-posta",
    icon: Mail,
    description: "Doğrulama ve Gravatar araması",
  },
  enrich: {
    label: "Otomatik Keşif",
    icon: Sparkles,
    description: "Bulunan ipuçlarını zincirleme genişletir",
  },
  llm: {
    label: "AI Profil",
    icon: Brain,
    description: "Claude ile kapsamlı profil özeti",
  },
  system: {
    label: "Sistem",
    icon: Globe,
    description: "",
  },
};

export default function NewAnalysisPage() {
  const [activeModules, setActiveModules] = useState<ModuleName[]>(["llm"]);
  const [previewImages, setPreviewImages] = useState<File[]>([]);

  return (
    <div>
      <TopBar
        title="Yeni Analiz"
        subtitle="Hedef verilerini girin ve analizi başlatın"
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="card"
        >
          <h2 className="font-display font-semibold mb-1 text-text-primary">
            Veri Girişi
          </h2>
          <p className="text-text-secondary text-sm mb-4">
            Tek ipucu yeter. Sistem <strong className="text-accent">3 tur</strong> derin
            tarama yapar: platform keşfi → e-posta/ihlal/kayıt tespiti → web dork + kimlik dosyası.
          </p>
          <InputPanel
            onPreviewChange={(modules, images) => {
              setActiveModules(modules);
              setPreviewImages(images);
            }}
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="space-y-4"
        >
          {previewImages.length > 0 && (
            <div className="card">
              <h3 className="text-sm font-medium text-text-secondary mb-3">
                Yüklenen Görseller
              </h3>
              <div className="grid grid-cols-3 gap-2">
                {previewImages.map((img, i) => (
                  <img
                    key={i}
                    src={URL.createObjectURL(img)}
                    alt={img.name}
                    className="w-full aspect-square object-cover rounded-lg border border-border"
                  />
                ))}
              </div>
            </div>
          )}

          <div className="card">
            <h3 className="text-sm font-medium text-text-secondary mb-3">
              Çalışacak Modüller
            </h3>
            <div className="space-y-2">
              {activeModules.map((mod, i) => {
                const info = MODULE_INFO[mod];
                if (!info) return null;
                const Icon = info.icon;
                return (
                  <motion.div
                    key={mod}
                    initial={{ opacity: 0, x: 10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="flex items-center gap-3 p-2 rounded-lg bg-bg-tertiary"
                  >
                    <Icon className="w-4 h-4 text-accent shrink-0" />
                    <div>
                      <p className="text-sm text-text-primary">{info.label}</p>
                      <p className="text-xs text-text-secondary">
                        {info.description}
                      </p>
                    </div>
                  </motion.div>
                );
              })}
              {activeModules.length === 1 && (
                <p className="text-xs text-text-secondary text-center py-2">
                  Veri girişi yapınca modüller otomatik güncellenir
                </p>
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
