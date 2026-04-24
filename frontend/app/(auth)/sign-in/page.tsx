import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "#f0f7f3",
      }}
    >
      <div>
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <h1 style={{ fontSize: 28, fontWeight: 700, color: "#1a5c2e" }}>
            Msingi
          </h1>
          <p style={{ color: "#666", marginTop: 4 }}>
            Retail Intelligence Platform
          </p>
        </div>
        <SignIn 
          afterSignInUrl="/dashboard"
          signUpUrl="/sign-up"
          appearance={{
            elements: {
              formButtonPrimary: {
                backgroundColor: "#1a5c2e",
              },
              card: {
                boxShadow: "none",
              },
            },
          }}
        />
      </div>
    </div>
  );
}