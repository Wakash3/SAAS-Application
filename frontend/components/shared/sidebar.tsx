"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { UserButton } from "@clerk/nextjs";

const nav = [
  { href: "/dashboard", label: "Overview", icon: "🏠" },
  { href: "/dashboard/pos", label: "POS", icon: "🛒" },
  { href: "/dashboard/fuel", label: "Fuel", icon: "⛽" },
  { href: "/dashboard/inventory", label: "Inventory", icon: "📦" },
  { href: "/dashboard/stocktake", label: "Stocktake", icon: "📋" },
  { href: "/dashboard/alerts", label: "Alerts", icon: "🔔" },
  { href: "/dashboard/reports", label: "Reports", icon: "📊" },
  { href: "/dashboard/erp", label: "ERP", icon: "🔗" },
  { href: "/dashboard/billing", label: "Billing", icon: "💳" },
  { href: "/dashboard/settings", label: "Settings", icon: "⚙️" },
];

export default function Sidebar() {
  const path = usePathname();
  return (
    <aside style={{ width: 220, background: "#1a5c2e", minHeight: "100vh",
      display: "flex", flexDirection: "column", padding: "20px 0" }}>
      <div style={{ padding: "0 20px 24px", borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
        <h1 style={{ color: "#fff", fontSize: 22, fontWeight: 700 }}>Msingi</h1>
        <p style={{ color: "rgba(255,255,255,0.5)", fontSize: 11, marginTop: 2 }}>
          Retail Intelligence
        </p>
      </div>
      <nav style={{ flex: 1, padding: "12px 8px" }}>
        {nav.map((item) => {
          const active = path === item.href || (item.href !== "/dashboard" && path.startsWith(item.href));
          return (
            <Link key={item.href} href={item.href}
              style={{ display: "flex", alignItems: "center", gap: 10,
                padding: "10px 12px", borderRadius: 8, marginBottom: 2,
                textDecoration: "none",
                background: active ? "rgba(255,255,255,0.15)" : "transparent",
                color: active ? "#fff" : "rgba(255,255,255,0.65)",
                fontSize: 14, fontWeight: active ? 600 : 400,
                transition: "all 0.15s" }}>
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
      <div style={{ padding: "16px 20px", borderTop: "1px solid rgba(255,255,255,0.1)" }}>
        <UserButton afterSignOutUrl="/sign-in" />
      </div>
    </aside>
  );
}