"use client";
import { useEffect, useState } from "react";
import { useApi } from "@/lib/api";

export default function SettingsPage() {
  const api = useApi();
  const [me, setMe] = useState<any>(null);
  useEffect(() => { api.get<any>("/api/v1/auth/me").then(setMe); }, []);

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 20 }}>Settings</h1>
      {me && (
        <div style={{ background: "#fff", borderRadius: 12, border: "1px solid #eee", padding: 24, maxWidth: 500 }}>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: "block", color: "#666", fontSize: 12, marginBottom: 4 }}>Organisation Name</label>
            <div style={{ fontWeight: 600 }}>{me.tenant?.name}</div>
          </div>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: "block", color: "#666", fontSize: 12, marginBottom: 4 }}>Plan</label>
            <div style={{ fontWeight: 600, textTransform: "capitalize" }}>{me.tenant?.plan}</div>
          </div>
          <div>
            <label style={{ display: "block", color: "#666", fontSize: 12, marginBottom: 8 }}>Branches</label>
            {me.branches?.map((b: any) => (
              <div key={b.id} style={{ padding: "8px 12px", background: "#f9fafb",
                borderRadius: 8, marginBottom: 8, fontSize: 13 }}>
                {b.name} {b.has_fuel && "⛽"}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}