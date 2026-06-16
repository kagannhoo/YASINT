"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { WSMessage } from "@/lib/types";
import { getWsUrl } from "@/lib/api";

const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 2000;

export function useWebSocket(
  analysisId: string | null,
  onMessage: (msg: WSMessage) => void
) {
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const retriesRef = useRef(0);
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  const connect = useCallback(() => {
    if (!analysisId) return;

    const ws = new WebSocket(getWsUrl(analysisId));
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      setError(null);
      retriesRef.current = 0;
    };

    ws.onmessage = (event) => {
      try {
        const msg: WSMessage = JSON.parse(event.data);
        onMessageRef.current(msg);
      } catch {
        // ignore parse errors
      }
    };

    ws.onerror = () => {
      setError("WebSocket bağlantı hatası");
    };

    ws.onclose = () => {
      setConnected(false);
      if (retriesRef.current < MAX_RETRIES && analysisId) {
        retriesRef.current += 1;
        setTimeout(() => connect(), RETRY_DELAY_MS * retriesRef.current);
      } else if (retriesRef.current >= MAX_RETRIES) {
        setError("Bağlantı kurulamadı. Sayfayı yenileyin.");
      }
    };
  }, [analysisId]);

  useEffect(() => {
    if (!analysisId) return;
    connect();

    const ping = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send("ping");
      }
    }, 30000);

    return () => {
      clearInterval(ping);
      wsRef.current?.close();
    };
  }, [analysisId, connect]);

  return { connected, error };
}
