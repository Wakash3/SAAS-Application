"use client";

import {
  SignInButton,
  SignUpButton,
  SignedIn,
  SignedOut,
  UserButton,
  OrganizationSwitcher,
  useUser,
} from "@clerk/nextjs";
import Link from "next/link";

export function NavBar() {
  const { isLoaded } = useUser();

  if (!isLoaded) {
    return (
      <nav className="flex justify-between items-center p-4 bg-white shadow-md">
        <Link href="/" className="text-xl font-bold text-blue-600">Msingi</Link>
        <div className="text-gray-500">Loading...</div>
      </nav>
    );
  }

  return (
    <nav className="flex justify-between items-center p-4 bg-white shadow-md">
      <Link href="/" className="text-xl font-bold text-blue-600">Msingi</Link>
      <div className="flex items-center gap-4">
        <SignedOut>
          <SignInButton mode="modal">
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              Sign In
            </button>
          </SignInButton>
          <SignUpButton mode="modal">
            <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
              Sign Up
            </button>
          </SignUpButton>
        </SignedOut>
        <SignedIn>
          <OrganizationSwitcher 
            afterSelectOrganizationUrl="/dashboard"
            afterCreateOrganizationUrl="/dashboard"
            appearance={{
              elements: {
                rootBox: "flex items-center",
                organizationSwitcherTrigger: "px-3 py-2 rounded-lg border border-gray-200 hover:bg-gray-50"
              }
            }}
          />
          <UserButton afterSignOutUrl="/" />
        </SignedIn>
      </div>
    </nav>
  );
}