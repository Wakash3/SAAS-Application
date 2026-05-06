import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  return (
    <div style={{ 
      minHeight: "100vh", 
      display: "flex", 
      alignItems: "center",
      justifyContent: "center", 
      background: "linear-gradient(135deg, #f0f7f3 0%, #e8f3ef 100%)",
      padding: "20px"
    }}>
      <div>
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <div style={{
            width: 60,
            height: 60,
            background: "#1a5c2e",
            borderRadius: "50%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            margin: "0 auto 16px",
            boxShadow: "0 4px 12px rgba(26, 92, 46, 0.2)"
          }}>
            <span style={{ fontSize: 30, color: "#fff" }}>M</span>
          </div>
          <h1 style={{ fontSize: 32, fontWeight: 700, color: "#1a5c2e", margin: 0 }}>
            Msingi
          </h1>
          <p style={{ color: "#666", marginTop: 8, fontSize: 14 }}>
            Create your account
          </p>
          <p style={{ color: "#888", marginTop: 4, fontSize: 12 }}>
            Join Kenya's leading retail intelligence platform
          </p>
        </div>
        <SignUp
          routing="hash"
          signInUrl="/sign-in"
          fallbackRedirectUrl="/dashboard"
          appearance={{
            elements: {
              rootBox: "mx-auto",
              card: "shadow-xl rounded-xl",
              headerTitle: "text-xl font-semibold",
              headerSubtitle: "text-sm",
              formButtonPrimary: "bg-[#1a5c2e] hover:bg-[#2d8c4a] text-white",
              footerActionLink: "text-[#1a5c2e] hover:text-[#2d8c4a]",
              socialButtonsBlockButton: "border-gray-300 hover:bg-gray-50",
            },
          }}
        />
      </div>
    </div>
  );
}