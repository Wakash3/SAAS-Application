"use client";
import { useEffect, useState } from "react";
import { useApi } from "@/lib/api";

interface FuelProduct {
  id: string; fuel_type: string; pump_number: number;
  current_stock_litres: number; tank_capacity_litres: number;
  price_per_litre: number; reorder_level_litres: number;
}

export default function FuelPage() {
  const api = useApi();
  const [fuels, setFuels] = useState<FuelProduct[]>([]);
  const [branchId, setBranchId] = useState("");

  useEffect(() => {
    api.get<any>("/api/v1/auth/me").then((me) => {
      const id = me.branches?.[0]?.id;
      if (id) {
        setBranchId(id);
        api.get<FuelProduct[]>(`/api/v1/fuel/?branch_id=${id}`).then(setFuels);
      }
    });
  }, [api]);

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 20 }}>Fuel Management</h1>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: 16 }}>
        {fuels.map((f) => {
          const pct = Math.round((f.current_stock_litres / f.tank_capacity_litres) * 100);
          const low = f.current_stock_litres <= f.reorder_level_litres;
          return (
            <div key={f.id} style={{ background: "#fff", borderRadius: 12,
              border: `1px solid ${low ? "#fca5a5" : "#eee"}`, padding: 20 }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
                <div>
                  <div style={{ fontWeight: 700, fontSize: 16 }}>{f.fuel_type}</div>
                  <div style={{ color: "#666", fontSize: 13 }}>Pump {f.pump_number}</div>
                </div>
                {low && <span style={{ background: "#fee2e2", color: "#dc2626",
                  padding: "3px 10px", borderRadius: 20, fontSize: 11, fontWeight: 600 }}>LOW</span>}
              </div>
              <div style={{ background: "#f0f7f3", borderRadius: 8, height: 12, marginBottom: 12 }}>
                <div style={{ background: "#1a5c2e", height: "100%", borderRadius: 8,
                  width: `${pct}%`, transition: "width 0.3s" }} />
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, fontSize: 13 }}>
                <div><div style={{ color: "#888" }}>Stock</div><strong>{f.current_stock_litres.toFixed(0)}L</strong></div>
                <div><div style={{ color: "#888" }}>Capacity</div><strong>{f.tank_capacity_litres}L</strong></div>
                <div><div style={{ color: "#888" }}>Price</div><strong>KES {f.price_per_litre}/L</strong></div>
                <div><div style={{ color: "#888" }}>Value</div>
                  <strong>KES {(f.current_stock_litres * f.price_per_litre).toLocaleString()}</strong></div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}