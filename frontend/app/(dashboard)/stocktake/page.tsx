"use client";
import { useEffect, useState } from "react";
import { useApi } from "@/lib/api";

export default function StocktakePage() {
  const api = useApi();
  const [snap, setSnap] = useState<any>(null);
  const [branchId, setBranchId] = useState("");

  useEffect(() => {
    api.get<any>("/api/v1/auth/me").then((me) => {
      const id = me.branches?.[0]?.id;
      if (id) {
        setBranchId(id);
        api.get<any>(`/api/v1/stocktake/latest?branch_id=${id}`).then(setSnap);
      }
    });
  }, []);

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 4 }}>Automated Stocktake</h1>
      <p style={{ color: "#666", marginBottom: 20 }}>System runs automatically at 6:00 AM daily.</p>
      {!snap?.snapshot && (
        <div style={{ background: "#f0f7f3", borderRadius: 12, padding: 24, textAlign: "center" }}>
          <p>No stocktake yet. The first snapshot will be generated tonight at 6am.</p>
        </div>
      )}
      {snap?.snapshot && (
        <div style={{ background: "#fff", borderRadius: 12, border: "1px solid #eee", overflow: "hidden" }}>
          <div style={{ padding: "16px 20px", background: "#f9fafb", borderBottom: "1px solid #eee",
            display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div style={{ fontWeight: 600 }}>Snapshot: {snap.snapshot.date}</div>
              <div style={{ fontSize: 13, color: "#666" }}>Type: {snap.snapshot.type}</div>
            </div>
            <span style={{ background: "#d1fae5", color: "#059669",
              padding: "4px 12px", borderRadius: 20, fontSize: 12, fontWeight: 600 }}>
              {snap.items.length} items
            </span>
          </div>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: "#f9fafb" }}>
                {["Product", "Type", "System Qty", "Physical Qty", "Variance", "Value KES", "Status"].map((h) => (
                  <th key={h} style={{ padding: "10px 16px", fontSize: 12,
                    color: "#666", fontWeight: 600, textAlign: "left", borderBottom: "1px solid #eee" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {snap.items.map((i: any) => (
                <tr key={i.id} style={{ borderBottom: "1px solid #f5f5f5" }}>
                  <td style={{ padding: "10px 16px", fontSize: 13 }}>{i.product_name}</td>
                  <td style={{ padding: "10px 16px", fontSize: 11, textTransform: "uppercase", color: "#888" }}>{i.item_type}</td>
                  <td style={{ padding: "10px 16px", fontSize: 13 }}>{i.system_qty}</td>
                  <td style={{ padding: "10px 16px", fontSize: 13 }}>{i.physical_qty ?? "—"}</td>
                  <td style={{ padding: "10px 16px", fontSize: 13,
                    color: i.variance < 0 ? "#dc2626" : i.variance > 0 ? "#059669" : "#666" }}>
                    {i.variance > 0 ? "+" : ""}{i.variance}
                  </td>
                  <td style={{ padding: "10px 16px", fontSize: 13 }}>
                    {i.variance_value_kes !== 0 ? `KES ${Math.abs(i.variance_value_kes).toFixed(0)}` : "—"}
                  </td>
                  <td style={{ padding: "10px 16px" }}>
                    <span style={{
                      background: i.status === "shortage" ? "#fee2e2" : i.status === "surplus" ? "#d1fae5" : "#f3f4f6",
                      color: i.status === "shortage" ? "#dc2626" : i.status === "surplus" ? "#059669" : "#6b7280",
                      padding: "2px 8px", borderRadius: 12, fontSize: 11, fontWeight: 600 }}>
                      {i.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}