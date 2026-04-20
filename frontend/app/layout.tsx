import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";

// Move CSS to a separate import that Next.js handles
import "./globals.css";

export const metadata: Metadata = {
  title: "Msingi Retail Intelligence",
  description: "Kenya-first retail SaaS",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  );
}