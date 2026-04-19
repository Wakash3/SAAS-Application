"use client";
import { useState, useRef, useEffect } from "react";
import { useAuth } from "@clerk/nextjs";
import { usePathname } from "next/navigation";

interface Message { role: "user" | "assistant"; content: string; }

function getPageContext(path: string) {
  if (path.includes("/pos")) return "pos";
  if (path.includes("/fuel")) return "fuel";
  if (path.includes("/inventory")) return "inventory";
  if (path.includes("/stocktake")) return "stocktake";
  if (path.includes("/alerts")) return "alerts";
  if (path.includes("/reports")) return "reports";
  if (path.includes("/erp")) return "erp";
  return "overview";
}

const SUGGESTIONS: Record<string, string[]> = {
  overview: ["Which branch had best margin?", "What is today revenue?"],
  pos: ["Do we have Kasuku 2kg?", "What is the price of Indomie?"],
  fuel: ["Which pump needs refilling?", "Pump 2 variance this week?"],
  inventory: ["What needs reordering now?", "Any out-of-stock items?"],
  stocktake: ["Show me last night variances", "Any fuel shortage?"],
  alerts: ["Why did this alert fire?", "What should I do?"],
  reports: ["Summarise this week for WhatsApp", "Top payment method?"],
  erp: ["What is owed to suppliers?", "Sync last sale to ERP"],
};

export default function Gladwell({ branchId }: { branchId?: string }) {
  const [open, setOpen] = useState(false);
  const [msgs, setMsgs] = useState<Message[]>([{
    role: "assistant",
    content: "Hey! I'm Gladwell, your retail intelligence analyst. Ask me anything about your business.",
  }]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const { getToken } = useAuth();
  const path = usePathname();
  const page = getPageContext(path);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs]);

  async function send() {
    const text = input.trim();
    if (!text || streaming) return;
    setInput("");
    const history = msgs.slice(1).map((m) => ({ role: m.role, content: m.content }));
    setMsgs((prev) => [...prev, { role: "user", content: text }]);
    setStreaming(true);
    setMsgs((prev) => [...prev, { role: "assistant", content: "" }]);

    try {
      const token = await getToken();
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/chat/message/stream`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
          body: JSON.stringify({ message: text, page_context: page, branch_id: branchId, conversation_history: history }),
        }
      );
      const reader = res.body!.getReader();
      const dec = new TextDecoder();
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        for (const line of dec.decode(value).split("\n")) {
          if (line.startsWith("data: ") && line !== "data: [DONE]") {
            try {
              const { text: t } = JSON.parse(line.slice(6));
              setMsgs((prev) => {
                const copy = [...prev];
                copy[copy.length - 1] = { ...copy[copy.length - 1], content: copy[copy.length - 1].content + t };
                return copy;
              });
            } catch {}
          }
        }
      }
    } catch {}
    finally { setStreaming(false); }
  }

  if (!open) return (
    <button onClick={() => setOpen(true)}
      style={{ position: "fixed", bottom: 24, right: 24, width: 52, height: 52,
        borderRadius: "50%", background: "#1a5c2e", border: "none", cursor: "pointer",
        color: "#fff", fontSize: 22, zIndex: 1000, boxShadow: "0 4px 16px rgba(0,0,0,0.2)" }}>
      ✦
    </button>
  );

  return (
    <div style={{ position: "fixed", bottom: 24, right: 24, width: 340,
      borderRadius: 16, zIndex: 1000, border: "1px solid #ddd", background: "#fff",
      display: "flex", flexDirection: "column", boxShadow: "0 4px 24px rgba(0,0,0,0.12)", maxHeight: 560 }}>
      <div style={{ background: "#1a5c2e", padding: "14px 16px", display: "flex",
        alignItems: "center", gap: 10, borderRadius: "16px 16px 0 0" }}>
        <div style={{ width: 32, height: 32, borderRadius: "50%",
          background: "rgba(255,255,255,0.2)", display: "flex",
          alignItems: "center", justifyContent: "center", color: "#fff" }}>✦</div>
        <div>
          <div style={{ color: "#fff", fontWeight: 600, fontSize: 14 }}>Gladwell</div>
          <div style={{ color: "rgba(255,255,255,0.7)", fontSize: 11 }}>AI Retail Analyst · {page}</div>
        </div>
        <button onClick={() => setOpen(false)}
          style={{ marginLeft: "auto", background: "none", border: "none",
            color: "rgba(255,255,255,0.7)", cursor: "pointer", fontSize: 20 }}>×</button>
      </div>
      <div style={{ flex: 1, overflowY: "auto", padding: 16, display: "flex", flexDirection: "column", gap: 10 }}>
        {msgs.map((m, i) => (
          <div key={i} style={{ display: "flex", justifyContent: m.role === "user" ? "flex-end" : "flex-start" }}>
            <div style={{ maxWidth: "84%", padding: "9px 13px",
              borderRadius: m.role === "user" ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
              background: m.role === "user" ? "#1a5c2e" : "#f5f5f5",
              color: m.role === "user" ? "#fff" : "#1a1a1a",
              fontSize: 13, lineHeight: 1.5, whiteSpace: "pre-wrap" }}>
              {m.content || (streaming && i === msgs.length - 1 ? "Thinking…" : "")}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      <div style={{ padding: "0 12px 8px", display: "flex", flexWrap: "wrap", gap: 6 }}>
        {(SUGGESTIONS[page] || []).map((q) => (
          <button key={q} onClick={() => setInput(q)}
            style={{ padding: "3px 10px", borderRadius: 20, border: "1px solid #1a5c2e",
              background: "none", color: "#1a5c2e", fontSize: 11, cursor: "pointer" }}>{q}</button>
        ))}
      </div>
      <div style={{ padding: 12, borderTop: "1px solid #eee", display: "flex", gap: 8 }}>
        <input value={input} onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Ask anything…"
          style={{ flex: 1, padding: "8px 12px", borderRadius: 8,
            border: "1px solid #ddd", fontSize: 13, outline: "none" }} />
        <button onClick={send} disabled={!input.trim() || streaming}
          style={{ width: 36, height: 36, borderRadius: 8,
            background: (!input.trim() || streaming) ? "#ccc" : "#1a5c2e",
            border: "none", color: "#fff", cursor: "pointer", fontSize: 16 }}>↑</button>
      </div>
    </div>
  );
}