"use client";
import { useEffect, useState } from "react";
import { useApi } from "@/lib/api";

export default function OverviewPage() {
  const api = useApi();
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    api.get("/api/v1/auth/me").then(setData).catch(console.error);
  }, []);

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8 }}>Dashboard Overview</h1>
      <p style={{ color: "#666", marginBottom: 24 }}>
        Welcome to Msingi — your retail intelligence platform.
      </p>
      {data && (
        <div style={{ background: "#fff", borderRadius: 12, padding: 20, border: "1px solid #eee" }}>
          <p><strong>Tenant:</strong> {data.tenant?.name}</p>
          <p><strong>Plan:</strong> {data.tenant?.plan}</p>
          <p><strong>Branches:</strong> {data.branches?.length}</p>
        </div>
      )}
      <p style={{ marginTop: 24, color: "#888", fontSize: 14 }}>
        💡 Ask Gladwell (bottom right) about today&apos;s sales, stock levels, or fuel status.
      </p>
    </div>
  );
}