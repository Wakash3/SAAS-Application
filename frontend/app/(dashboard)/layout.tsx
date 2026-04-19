import Sidebar from "@/components/shared/sidebar";
import Gladwell from "@/components/gladwell/gladwell";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <Sidebar />
      <main style={{ flex: 1, padding: 24, overflowY: "auto" }}>
        {children}
      </main>
      <Gladwell />
    </div>
  );
}