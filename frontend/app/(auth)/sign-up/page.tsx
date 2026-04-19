import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center",
      justifyContent: "center", background: "#f0f7f3" }}>
      <div>
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <h1 style={{ fontSize: 28, fontWeight: 700, color: "#1a5c2e" }}>Msingi</h1>
          <p style={{ color: "#666", marginTop: 4 }}>Create your account</p>
        </div>
        <SignUp afterSignUpUrl="/dashboard" />
      </div>
    </div>
  );
}