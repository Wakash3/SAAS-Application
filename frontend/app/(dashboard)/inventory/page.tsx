"use client";
import { useEffect, useState } from "react";
import { useApi } from "@/lib/api";

export default function InventoryPage() {
  const api = useApi();
  const [data, setData] = useState<any>(null);
  const [branchId, setBranchId] = useState("");

  useEffect(() => {
    api.get<any>("/api/v1/auth/me").then((me) => {
      const id = me.branches?.[0]?.id;
      if (id) {
        setBranchId(id);
        api.get<any>(`/api/v1/inventory/summary?branch_id=${id}`).then(setData);
      }
    });
  }, []);

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 20 }}>Inventory</h1>
      {data && (
        <>
          <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 12 }}>FMCG Products</h2>
          <table style={{ width: "100%", background: "#fff", borderRadius: 12,
            border: "1px solid #eee", borderCollapse: "collapse", marginBottom: 24 }}>
            <thead>
              <tr style={{ background: "#f9fafb", textAlign: "left" }}>
                {["Product", "Stock", "Reorder At", "Value KES", "Status"].map((h) => (
                  <th key={h} style={{ padding: "12px 16px", fontSize: 12, color: "#666",
                    fontWeight: 600, borderBottom: "1px solid #eee" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.fmcg.map((p: any) => (
                <tr key={p.id}>
                  <td style={{ padding: "12px 16px", fontSize: 14 }}>{p.name}</td>
                  <td style={{ padding: "12px 16px", fontSize: 14 }}>{p.stock}</td>
                  <td style={{ padding: "12px 16px", fontSize: 14 }}>{p.reorder_level}</td>
                  <td style={{ padding: "12px 16px", fontSize: 14 }}>KES {p.value_kes.toLocaleString()}</td>
                  <td style={{ padding: "12px 16px" }}>
                    <span style={{ background: p.low ? "#fee2e2" : "#d1fae5",
                      color: p.low ? "#dc2626" : "#059669",
                      padding: "3px 10px", borderRadius: 20, fontSize: 11, fontWeight: 600 }}>
                      {p.low ? "Low Stock" : "OK"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}