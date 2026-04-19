import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
// @ts-ignore
import "./globals.css";

export const metadata: Metadata = {
  title: "Msingi Retail Intelligence",
  description: "Kenya-first retail SaaS for petroleum stations and convenience stores",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <head>
        </head>
        <body>{children}</body>
      </html>
    </ClerkProvider>
  );
}