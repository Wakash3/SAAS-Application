"use client";
import { useState } from "react";
import { useApi } from "@/lib/api";

export default function ERPPage() {
  const api = useApi();
  const [webhookUrl, setWebhookUrl] = useState("");
  const [result, setResult] = useState("");

  async function sync() {
    try {
      const me = await api.get<any>("/api/v1/auth/me");
      const id = me.branches?.[0]?.id;
      const r = await api.post<any>(`/api/v1/erp/sync/webhook?branch_id=${id}`, { webhook_url: webhookUrl });
      setResult(`✅ Synced ${r.synced} sales (HTTP ${r.status})`);
    } catch (e: any) {
      setResult(`❌ ${e.message}`);
    }
  }

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8 }}>ERP Integration</h1>
      <p style={{ color: "#666", marginBottom: 24 }}>Push sales data to QuickBooks, Odoo, or any webhook endpoint.</p>
      <div style={{ background: "#fff", borderRadius: 12, border: "1px solid #eee", padding: 24, maxWidth: 500 }}>
        <label style={{ display: "block", fontWeight: 600, marginBottom: 8 }}>Webhook URL</label>
        <input value={webhookUrl} onChange={(e) => setWebhookUrl(e.target.value)}
          placeholder="https://your-erp.com/api/sales"
          style={{ width: "100%", padding: "10px 12px", borderRadius: 8,
            border: "1px solid #ddd", fontSize: 14, marginBottom: 16 }} />
        <button onClick={sync}
          style={{ padding: "10px 20px", background: "#1a5c2e", color: "#fff",
            border: "none", borderRadius: 8, cursor: "pointer", fontWeight: 600 }}>
          Sync Last 10 Sales
        </button>
        {result && <div style={{ marginTop: 16, padding: 12, background: "#f0f7f3", borderRadius: 8 }}>{result}</div>}
      </div>
    </div>
  );
}