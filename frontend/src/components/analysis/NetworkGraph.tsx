"use client";

import { useMemo } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  type Node,
  type Edge,
} from "reactflow";
import "reactflow/dist/style.css";
import type { Finding } from "@/lib/types";

interface NetworkGraphProps {
  findings: Finding[];
  targetName?: string;
}

export function NetworkGraph({ findings, targetName }: NetworkGraphProps) {
  const { nodes, edges } = useMemo(() => {
    const socialFindings = findings.filter((f) => f.category === "social");
    const centerName = targetName || "Hedef";

    const nodes: Node[] = [
      {
        id: "center",
        data: { label: centerName },
        position: { x: 250, y: 200 },
        style: {
          background: "#00d4aa20",
          border: "1px solid #00d4aa",
          borderRadius: "8px",
          color: "#e8eaf0",
          padding: "10px",
          fontSize: "14px",
          fontWeight: "bold",
        },
      },
    ];

    const edges: Edge[] = [];

    socialFindings.forEach((f, i) => {
      const angle = (i / Math.max(socialFindings.length, 1)) * 2 * Math.PI;
      const radius = 150;
      const id = `node-${i}`;
      const platform = f.key.replace("account_", "");

      nodes.push({
        id,
        data: { label: platform },
        position: {
          x: 250 + Math.cos(angle) * radius,
          y: 200 + Math.sin(angle) * radius,
        },
        style: {
          background: "#111318",
          border: "1px solid #2a2d35",
          borderRadius: "8px",
          color: "#8b8f9e",
          padding: "8px",
          fontSize: "12px",
        },
      });

      edges.push({
        id: `edge-${i}`,
        source: "center",
        target: id,
        style: { stroke: "#00d4aa40" },
      });
    });

    return { nodes, edges };
  }, [findings, targetName]);

  if (nodes.length <= 1) {
    return (
      <div className="card h-64 flex items-center justify-center text-text-secondary text-sm">
        Sosyal ağ verisi bulunamadı
      </div>
    );
  }

  return (
    <div className="h-80 rounded-card border border-border overflow-hidden">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#2a2d35" gap={20} />
        <Controls />
        <MiniMap
          nodeColor="#00d4aa"
          maskColor="#0a0b0d80"
          style={{ background: "#111318" }}
        />
      </ReactFlow>
    </div>
  );
}
