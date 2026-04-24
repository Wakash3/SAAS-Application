"use client";

import { SignInButton, SignUpButton, SignedIn, SignedOut, UserButton } from "@clerk/nextjs";
import Link from "next/link";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50">
      <div className="text-center max-w-md p-8 bg-white rounded-lg shadow">
        <h1 className="text-4xl font-bold text-blue-600 mb-4">Msingi</h1>
        <p className="text-gray-600 mb-8">
          Retail Intelligence Platform for Petroleum Stations and Convenience Stores
        </p>
        
        <SignedOut>
          <div className="space-y-4">
            <SignUpButton mode="modal">
              <button className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                Get Started - Sign Up
              </button>
            </SignUpButton>
            <SignInButton mode="modal">
              <button className="w-full px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">
                Sign In
              </button>
            </SignInButton>
          </div>
        </SignedOut>
        
        <SignedIn>
          <div className="space-y-4">
            <Link href="/dashboard">
              <button className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                Go to Dashboard
              </button>
            </Link>
            <div className="flex justify-center">
              <UserButton afterSignOutUrl="/" />
            </div>
          </div>
        </SignedIn>
      </div>
    </div>
  );
}