"use client";

import { useEffect, useRef } from "react";
import type { Location } from "@/lib/types";

interface MapViewProps {
  locations: Location[];
  height?: string;
}

const SOURCE_COLORS: Record<string, string> = {
  exif_gps: "#10b981",
  ip_geo: "#3b82f6",
  visual_estimate: "#f59e0b",
  social_checkin: "#a855f7",
};

export function MapView({ locations, height = "400px" }: MapViewProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<L.Map | null>(null);

  useEffect(() => {
    if (!mapRef.current || typeof window === "undefined") return;

    let cancelled = false;

    import("leaflet").then((L) => {
      if (cancelled || !mapRef.current) return;

      import("leaflet/dist/leaflet.css");

      if (mapInstance.current) {
        mapInstance.current.remove();
      }

      const defaultCenter: [number, number] =
        locations.length > 0
          ? [locations[0].latitude, locations[0].longitude]
          : [39.0, 35.0];

      const map = L.map(mapRef.current).setView(defaultCenter, locations.length ? 10 : 6);
      mapInstance.current = map;

      L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>',
      }).addTo(map);

      locations.forEach((loc) => {
        const color = SOURCE_COLORS[loc.source] || "#ef4444";
        const icon = L.divIcon({
          className: "custom-marker",
          html: `<div style="width:16px;height:16px;background:${color};border-radius:50%;border:2px solid white;box-shadow:0 0 8px ${color}"></div>`,
          iconSize: [16, 16],
          iconAnchor: [8, 8],
        });

        L.marker([loc.latitude, loc.longitude], { icon })
          .bindPopup(
            `<b>${loc.source}</b><br/>${loc.latitude.toFixed(4)}, ${loc.longitude.toFixed(4)}${
              loc.address ? `<br/>${loc.address}` : ""
            }`
          )
          .addTo(map);
      });
    });

    return () => {
      cancelled = true;
      mapInstance.current?.remove();
      mapInstance.current = null;
    };
  }, [locations]);

  return (
    <div className="relative rounded-card overflow-hidden border border-border">
      <div ref={mapRef} style={{ height, width: "100%" }} />
      {locations.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center bg-bg-tertiary/80">
          <p className="text-text-secondary text-sm">Konum verisi bulunamadı</p>
        </div>
      )}
      <div className="absolute bottom-3 left-3 flex gap-2 text-xs">
        {Object.entries(SOURCE_COLORS).map(([source, color]) => (
          <span key={source} className="flex items-center gap-1 bg-bg-secondary/90 px-2 py-1 rounded">
            <span className="w-2 h-2 rounded-full" style={{ background: color }} />
            {source.replace("_", " ")}
          </span>
        ))}
      </div>
    </div>
  );
}
