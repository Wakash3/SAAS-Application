"use client";
import { useEffect, useState } from "react";
import { useApi } from "@/lib/api";

export default function AlertsPage() {
  const api = useApi();
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    api.get<any>("/api/v1/auth/me").then((me) => {
      const id = me.branches?.[0]?.id;
      if (id) {
        Promise.all([
          api.get<any>(`/api/v1/inventory/summary?branch_id=${id}`),
          api.get<any>(`/api/v1/fuel/?branch_id=${id}`),
        ]).then(([inv, fuel]) => setData({ inv, fuel }));
      }
    });
  }, [api]);

  const lowFmcg = data?.inv?.fmcg?.filter((p: any) => p.low) || [];
  const lowFuel = data?.fuel?.filter((f: any) => f.low) || [];

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 20 }}>Alerts</h1>
      {lowFmcg.length === 0 && lowFuel.length === 0 && (
        <div style={{ background: "#d1fae5", borderRadius: 12, padding: 20, color: "#059669" }}>
          ✅ All stock levels are above reorder points.
        </div>
      )}
      {lowFmcg.map((p: any) => (
        <div key={p.id} style={{ background: "#fff", border: "1px solid #fca5a5",
          borderRadius: 12, padding: 16, marginBottom: 12, display: "flex",
          justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <div style={{ fontWeight: 600 }}>⚠️ Low Stock: {p.name}</div>
            <div style={{ color: "#666", fontSize: 13 }}>Current: {p.stock} | Reorder at: {p.reorder_level}</div>
          </div>
          <span style={{ background: "#fee2e2", color: "#dc2626",
            padding: "4px 12px", borderRadius: 20, fontSize: 12, fontWeight: 600 }}>FMCG</span>
        </div>
      ))}
      {lowFuel.map((f: any) => (
        <div key={f.id} style={{ background: "#fff", border: "1px solid #fca5a5",
          borderRadius: 12, padding: 16, marginBottom: 12, display: "flex",
          justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <div style={{ fontWeight: 600 }}>⛽ Low Fuel: {f.type} Pump {f.pump}</div>
            <div style={{ color: "#666", fontSize: 13 }}>
              Current: {f.stock_L.toFixed(0)}L | Value: KES {f.value_kes.toLocaleString()}
            </div>
          </div>
          <span style={{ background: "#fef3c7", color: "#d97706",
            padding: "4px 12px", borderRadius: 20, fontSize: 12, fontWeight: 600 }}>FUEL</span>
        </div>
      ))}
    </div>
  );
}