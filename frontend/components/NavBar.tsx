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

export function NavBar() {
  const { isLoaded } = useUser();

  if (!isLoaded) {
    return (
      <nav className="flex justify-between items-center p-4 bg-white shadow-md">
        <div className="text-xl font-bold text-blue-600">Msingi</div>
        <div className="text-gray-500">Loading...</div>
      </nav>
    );
  }

  return (
    <nav className="flex justify-between items-center p-4 bg-white shadow-md">
      <div className="text-xl font-bold text-blue-600">Msingi</div>
      <div className="flex items-center gap-4">
        <SignedOut>
          <SignInButton mode="modal">
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              Sign In
            </button>
          </SignInButton>
          <SignUpButton mode="modal">
            <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
              Sign Up
            </button>
          </SignUpButton>
        </SignedOut>
        <SignedIn>
          <OrganizationSwitcher 
            afterSelectOrganizationUrl="/dashboard"
            afterCreateOrganizationUrl="/dashboard"
          />
          <UserButton afterSignOutUrl="/" />
        </SignedIn>
      </div>
    </nav>
  );
}