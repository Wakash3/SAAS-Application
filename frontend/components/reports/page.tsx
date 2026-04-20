"use client";
import { useEffect, useState } from "react";
import { useApi } from "@/lib/api";

export default function ReportsPage() {
  const api = useApi();
  const [data, setData] = useState<any>(null);
  const [days, setDays] = useState(7);

  useEffect(() => {
    api.get<any>("/api/v1/auth/me").then((me) => {
      const id = me.branches?.[0]?.id;
      if (id) api.get<any>(`/api/v1/reports/summary?branch_id=${id}&days=${days}`).then(setData);
    });
  }, [days, api]);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700 }}>Reports</h1>
        <select value={days} onChange={(e) => setDays(Number(e.target.value))}
          style={{ padding: "8px 12px", borderRadius: 8, border: "1px solid #ddd" }}>
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>
      {data && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 16 }}>
          <div style={{ background: "#fff", borderRadius: 12, border: "1px solid #eee", padding: 20 }}>
            <div style={{ color: "#666", fontSize: 13 }}>Total Revenue</div>
            <div style={{ fontSize: 28, fontWeight: 700, color: "#1a5c2e", marginTop: 4 }}>
              KES {data.total_revenue_kes.toLocaleString()}
            </div>
            <div style={{ fontSize: 12, color: "#888", marginTop: 4 }}>Last {data.period_days} days</div>
          </div>
          {Object.entries(data.by_payment_method || {}).map(([method, amount]: any) => (
            <div key={method} style={{ background: "#fff", borderRadius: 12, border: "1px solid #eee", padding: 20 }}>
              <div style={{ color: "#666", fontSize: 13, textTransform: "capitalize" }}>{method} Sales</div>
              <div style={{ fontSize: 24, fontWeight: 700, marginTop: 4 }}>
                KES {amount.toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}