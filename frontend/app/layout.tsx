import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import { NavBar } from "../components/NavBar";
import "./globals.css";

export const metadata: Metadata = {
  title: "Msingi Retail Intelligence",
  description: "Kenya-first retail SaaS for petroleum stations and convenience stores",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body className="bg-gray-50">
          <NavBar />
          <main className="min-h-screen">
            {children}
          </main>
        </body>
      </html>
    </ClerkProvider>
  );
}