"use client";
import { useEffect, useState } from "react";
import { useApi } from "@/lib/api";

const PLANS = [
  { name: "Starter", price: "KES 2,500/mo", features: ["1 branch", "POS + FMCG", "M-Pesa", "2 cashiers"] },
  { name: "Growth", price: "KES 6,500/mo", features: ["5 branches", "Fuel + petroleum", "All Gladwell pages", "Daily stocktake", "ERP webhook", "10 cashiers"] },
  { name: "Enterprise", price: "Custom", features: ["Unlimited branches", "Real-time stocktake", "QuickBooks/Odoo", "API access", "Dedicated support"] },
];

export default function BillingPage() {
  const api = useApi();
  const [plan, setPlan] = useState("");
  useEffect(() => { api.get<any>("/api/v1/auth/me").then((me) => setPlan(me.tenant?.plan)); }, []);

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8 }}>Subscription</h1>
      <p style={{ color: "#666", marginBottom: 24 }}>Current plan: <strong style={{ color: "#1a5c2e" }}>{plan}</strong></p>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: 16 }}>
        {PLANS.map((p) => (
          <div key={p.name} style={{ background: "#fff", borderRadius: 12,
            border: `2px solid ${plan === p.name.toLowerCase() ? "#1a5c2e" : "#eee"}`, padding: 24 }}>
            <div style={{ fontWeight: 700, fontSize: 18, marginBottom: 4 }}>{p.name}</div>
            <div style={{ color: "#1a5c2e", fontWeight: 700, fontSize: 20, marginBottom: 16 }}>{p.price}</div>
            {p.features.map((f) => (
              <div key={f} style={{ fontSize: 13, color: "#444", marginBottom: 6 }}>✓ {f}</div>
            ))}
            {plan !== p.name.toLowerCase() && (
              <button style={{ marginTop: 16, width: "100%", padding: 10,
                background: "#1a5c2e", color: "#fff", border: "none",
                borderRadius: 8, cursor: "pointer", fontWeight: 600 }}>
                Upgrade
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}