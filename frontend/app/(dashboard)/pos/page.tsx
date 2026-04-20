"use client";
import { useEffect, useState } from "react";
import { useApi } from "@/lib/api";

interface Product { id: string; name: string; sku: string; selling_price: number; current_stock: number; }
interface CartItem extends Product { qty: number; }

export default function POSPage() {
  const api = useApi();
  const [products, setProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [branchId, setBranchId] = useState("");
  const [status, setStatus] = useState("");

  useEffect(() => {
    api.get<any>("/api/v1/auth/me").then((me) => {
      const id = me.branches?.[0]?.id;
      if (id) {
        setBranchId(id);
        api.get<Product[]>(`/api/v1/products/?branch_id=${id}`).then(setProducts);
      }
    });
  }, [api]);

  function addToCart(p: Product) {
    setCart((prev) => {
      const ex = prev.find((i) => i.id === p.id);
      if (ex) return prev.map((i) => i.id === p.id ? { ...i, qty: i.qty + 1 } : i);
      return [...prev, { ...p, qty: 1 }];
    });
  }

  const total = cart.reduce((s, i) => s + i.selling_price * i.qty, 0);

  async function checkout(method: string) {
    if (!cart.length) return;
    try {
      const result = await api.post<any>("/api/v1/sales/", {
        branch_id: branchId,
        cashier_id: "cashier_001",
        payment_method: method,
        items: cart.map((i) => ({
          item_type: "fmcg",
          product_id: i.id,
          quantity: i.qty,
          unit_price: i.selling_price,
        })),
      });
      setStatus(`✅ Sale ${result.sale_number} completed — KES ${total.toFixed(2)}`);
      setCart([]);
    } catch (e: any) {
      setStatus(`❌ ${e.message}`);
    }
  }

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 20 }}>POS Terminal</h1>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 320px", gap: 20 }}>
        {/* Product Grid */}
        <div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", gap: 12 }}>
            {products.map((p) => (
              <button key={p.id} onClick={() => addToCart(p)}
                style={{ background: "#fff", border: "1px solid #eee", borderRadius: 10,
                  padding: 14, cursor: "pointer", textAlign: "left",
                  opacity: p.current_stock <= 0 ? 0.4 : 1 }}
                disabled={p.current_stock <= 0}>
                <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 4 }}>{p.name}</div>
                <div style={{ color: "#1a5c2e", fontWeight: 700 }}>KES {p.selling_price}</div>
                <div style={{ color: "#888", fontSize: 11 }}>Stock: {p.current_stock}</div>
              </button>
            ))}
          </div>
        </div>
        {/* Cart */}
        <div style={{ background: "#fff", borderRadius: 12, border: "1px solid #eee", padding: 16 }}>
          <h2 style={{ fontWeight: 700, marginBottom: 12 }}>Cart</h2>
          {cart.length === 0 && <p style={{ color: "#888", fontSize: 13 }}>No items added</p>}
          {cart.map((i) => (
            <div key={i.id} style={{ display: "flex", justifyContent: "space-between",
              padding: "8px 0", borderBottom: "1px solid #f0f0f0", fontSize: 13 }}>
              <span>{i.name} ×{i.qty}</span>
              <span>KES {(i.selling_price * i.qty).toFixed(2)}</span>
            </div>
          ))}
          <div style={{ marginTop: 16, fontWeight: 700, fontSize: 16 }}>Total: KES {total.toFixed(2)}</div>
          <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
            <button onClick={() => checkout("cash")}
              style={{ flex: 1, padding: 10, background: "#1a5c2e", color: "#fff",
                border: "none", borderRadius: 8, cursor: "pointer", fontWeight: 600 }}>
              Cash
            </button>
            <button onClick={() => checkout("mpesa")}
              style={{ flex: 1, padding: 10, background: "#00a651", color: "#fff",
                border: "none", borderRadius: 8, cursor: "pointer", fontWeight: 600 }}>
              M-Pesa
            </button>
          </div>
          {status && (
            <div style={{ marginTop: 12, padding: 10, background: "#f0f7f3",
              borderRadius: 8, fontSize: 13 }}>{status}</div>
          )}
        </div>
      </div>
    </div>
  );
}