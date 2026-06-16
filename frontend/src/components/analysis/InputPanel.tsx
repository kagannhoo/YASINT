"use client";

import { useCallback, useState } from "react";
import { useRouter } from "next/navigation";
import { Upload, X, Loader2 } from "lucide-react";
import { startAnalysis } from "@/lib/api";
import type { ModuleName } from "@/lib/types";

interface InputPanelProps {
  onPreviewChange?: (modules: ModuleName[], images: File[]) => void;
}

export function InputPanel({ onPreviewChange }: InputPanelProps) {
  const router = useRouter();
  const [images, setImages] = useState<File[]>([]);
  const [username, setUsername] = useState("");
  const [ipAddress, setIpAddress] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [targetName, setTargetName] = useState("");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  const getActiveModules = useCallback((): ModuleName[] => {
    const modules: ModuleName[] = [];
    if (images.length > 0) {
      modules.push("exif", "face", "geo", "reverse_image");
    }
    if (username) modules.push("username", "social");
    if (ipAddress) modules.push("ip");
    if (email) modules.push("email");
    if (phone) modules.push("phone");
    modules.push("llm");
    return modules;
  }, [images, username, ipAddress, email]);

  const updatePreview = useCallback(
    (imgs: File[]) => {
      const modules: ModuleName[] = [];
      if (imgs.length > 0) modules.push("exif", "face", "geo", "reverse_image");
      if (username) modules.push("username", "social");
      if (ipAddress) modules.push("ip");
      if (email) modules.push("email");
      modules.push("llm");
      onPreviewChange?.(modules, imgs);
    },
    [username, ipAddress, email, phone, onPreviewChange]
  );

  const handleFiles = (files: FileList | null) => {
    if (!files) return;
    const newImages = [...images, ...Array.from(files)].slice(0, 10);
    setImages(newImages);
    updatePreview(newImages);
  };

  const removeImage = (index: number) => {
    const newImages = images.filter((_, i) => i !== index);
    setImages(newImages);
    updatePreview(newImages);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!images.length && !username && !ipAddress && !email && !phone) {
      setError("En az bir veri girişi gerekli");
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      images.forEach((img) => formData.append("images", img));
      if (username) formData.append("username", username);
      if (ipAddress) formData.append("ip_address", ipAddress);
      if (email) formData.append("email", email);
      if (phone) formData.append("phone", phone);
      if (targetName) formData.append("target_name", targetName);
      if (notes) formData.append("notes", notes);

      const result = await startAnalysis(formData);
      router.push(`/analysis/${result.analysis_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analiz başlatılamadı");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div
        className={`border-2 border-dashed rounded-card p-8 text-center transition-colors cursor-pointer ${
          dragOver
            ? "border-accent bg-accent-dim"
            : "border-border hover:border-accent/50"
        }`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          handleFiles(e.dataTransfer.files);
        }}
        onClick={() => document.getElementById("file-input")?.click()}
      >
        <Upload className="w-10 h-10 text-accent mx-auto mb-3" />
        <p className="text-text-primary font-medium">Fotoğraf Yükle</p>
        <p className="text-text-secondary text-sm mt-1">
          Sürükle-bırak veya tıkla (çoklu dosya)
        </p>
        <input
          id="file-input"
          type="file"
          accept="image/*"
          multiple
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
      </div>

      {images.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {images.map((img, i) => (
            <div key={i} className="relative group">
              <img
                src={URL.createObjectURL(img)}
                alt={img.name}
                className="w-16 h-16 object-cover rounded-lg border border-border"
              />
              <button
                type="button"
                onClick={() => removeImage(i)}
                className="absolute -top-1 -right-1 bg-danger rounded-full p-0.5 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <X className="w-3 h-3 text-white" />
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="space-y-4">
        <div>
          <label className="block text-sm text-text-secondary mb-1.5">
            Kullanıcı Adı
          </label>
          <input
            type="text"
            className="input-field"
            placeholder="@kullaniciadi"
            value={username}
            onChange={(e) => {
              setUsername(e.target.value);
              updatePreview(images);
            }}
          />
        </div>

        <div>
          <label className="block text-sm text-text-secondary mb-1.5">
            IP Adresi / Domain
          </label>
          <input
            type="text"
            className="input-field font-mono"
            placeholder="192.168.1.1 veya example.com"
            value={ipAddress}
            onChange={(e) => {
              setIpAddress(e.target.value);
              updatePreview(images);
            }}
          />
        </div>

        <div>
          <label className="block text-sm text-text-secondary mb-1.5">
            E-posta Adresi
          </label>
          <input
            type="email"
            className="input-field"
            placeholder="ornek@email.com"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              updatePreview(images);
            }}
          />
        </div>

        <div>
          <label className="block text-sm text-text-secondary mb-1.5">
            Telefon Numarası
          </label>
          <input
            type="tel"
            className="input-field font-mono"
            placeholder="+90 5XX XXX XX XX"
            value={phone}
            onChange={(e) => {
              setPhone(e.target.value);
              updatePreview(images);
            }}
          />
        </div>

        <div>
          <label className="block text-sm text-text-secondary mb-1.5">
            Hedef İsim (opsiyonel)
          </label>
          <input
            type="text"
            className="input-field"
            placeholder="Raporlama için isim"
            value={targetName}
            onChange={(e) => setTargetName(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm text-text-secondary mb-1.5">
            Notlar
          </label>
          <textarea
            className="input-field resize-none h-24"
            placeholder="Ek notlar..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </div>
      </div>

      {error && (
        <div className="bg-danger/10 border border-danger/30 text-danger text-sm rounded-lg p-3">
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={loading}
        className="btn-primary w-full flex items-center justify-center gap-2 text-lg py-4 bg-gradient-to-r from-accent to-emerald-400"
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Başlatılıyor...
          </>
        ) : (
          "Analizi Başlat"
        )}
      </button>
    </form>
  );
}
