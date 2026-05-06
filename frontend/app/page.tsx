import Link from "next/link";

export default function HomePage() {
  return (
    <div 
      style={{ 
        minHeight: "100vh", 
        display: "flex", 
        alignItems: "center",
        justifyContent: "center", 
        background: "linear-gradient(135deg, #f0f7f3 0%, #e8f3ef 100%)",
        flexDirection: "column", 
        gap: 32,
        padding: "20px"
      }}
    >
      <div style={{ textAlign: "center" }}>
        {/* Logo */}
        <div style={{ marginBottom: 24 }}>
          <div style={{ 
            width: 80, 
            height: 80, 
            background: "#1a5c2e", 
            borderRadius: "50%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            margin: "0 auto",
            boxShadow: "0 4px 12px rgba(26, 92, 46, 0.2)"
          }}>
            <span style={{ fontSize: 40, color: "#fff" }}>M</span>
          </div>
        </div>
        
        <h1 style={{ 
          fontSize: 56, 
          fontWeight: 800, 
          color: "#1a5c2e",
          margin: 0,
          letterSpacing: "-0.02em"
        }}>
          Msingi
        </h1>
        
        <p style={{ 
          color: "#4a5568", 
          fontSize: 20, 
          marginTop: 12,
          fontWeight: 500
        }}>
          Retail Intelligence Platform
        </p>
        
        <p style={{ 
          color: "#718096", 
          fontSize: 15, 
          marginTop: 8,
          maxWidth: 500,
          marginLeft: "auto",
          marginRight: "auto"
        }}>
          Kenya-first · Petroleum POS · AI Analyst · M-Pesa
        </p>
      </div>
      
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap", justifyContent: "center" }}>
        <Link 
          href="/sign-in"
          style={{ 
            padding: "14px 36px", 
            background: "#1a5c2e", 
            color: "#fff",
            borderRadius: 10, 
            textDecoration: "none", 
            fontWeight: 600, 
            fontSize: 16,
            display: "inline-block",
            boxShadow: "0 2px 4px rgba(0,0,0,0.1)"
          }}
        >
          Sign In
        </Link>
        
        <Link 
          href="/sign-up"
          style={{ 
            padding: "14px 36px", 
            background: "#fff", 
            color: "#1a5c2e",
            borderRadius: 10, 
            textDecoration: "none", 
            fontWeight: 600, 
            fontSize: 16,
            border: "2px solid #1a5c2e",
            display: "inline-block"
          }}
        >
          Sign Up
        </Link>
      </div>
      
      {/* Feature highlights */}
      <div style={{ 
        marginTop: 48,
        display: "flex", 
        gap: 24, 
        flexWrap: "wrap", 
        justifyContent: "center",
        maxWidth: 900,
        padding: "0 20px"
      }}>
        <div style={{ textAlign: "center", flex: "1", minWidth: 150 }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>📊</div>
          <div style={{ fontWeight: 600, color: "#2d3748", marginBottom: 4 }}>Real-time Analytics</div>
          <div style={{ fontSize: 12, color: "#718096" }}>AI-powered insights</div>
        </div>
        <div style={{ textAlign: "center", flex: "1", minWidth: 150 }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>🏪</div>
          <div style={{ fontWeight: 600, color: "#2d3748", marginBottom: 4 }}>POS Integration</div>
          <div style={{ fontSize: 12, color: "#718096" }}>Seamless checkout</div>
        </div>
        <div style={{ textAlign: "center", flex: "1", minWidth: 150 }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>💳</div>
          <div style={{ fontWeight: 600, color: "#2d3748", marginBottom: 4 }}>M-Pesa Ready</div>
          <div style={{ fontSize: 12, color: "#718096" }}>Mobile payments</div>
        </div>
        <div style={{ textAlign: "center", flex: "1", minWidth: 150 }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>⛽</div>
          <div style={{ fontWeight: 600, color: "#2d3748", marginBottom: 4 }}>Fuel Management</div>
          <div style={{ fontSize: 12, color: "#718096" }}>Petroleum focus</div>
        </div>
      </div>
      
      {/* Footer */}
      <div style={{ 
        marginTop: 64,
        paddingTop: 24,
        borderTop: "1px solid #e2e8f0",
        textAlign: "center",
        color: "#a0aec0",
        fontSize: 13
      }}>
        © 2024 Msingi Retail Intelligence Platform. All rights reserved.
      </div>
    </div>
  );
}
