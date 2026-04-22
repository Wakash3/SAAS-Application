"use client";

import { useOrganization, useUser,OrganizationSwitcher } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function CreateOrganizationPage() {
  const { isLoaded: isOrgLoaded, organization } = useOrganization();
  const { isLoaded: isUserLoaded } = useUser();
  const router = useRouter();

  useEffect(() => {
    if (isOrgLoaded && organization) {
      router.push("/dashboard");
    }
  }, [isOrgLoaded, organization, router]);

  if (!isUserLoaded || !isOrgLoaded) {
    return <div className="p-8 text-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full">
        <h1 className="text-2xl font-bold mb-6 text-center">Create Your Organization</h1>
        <p className="text-gray-600 mb-6 text-center">
          Set up your retail business to start using Msingi
        </p>
        <OrganizationSwitcher 
          afterCreateOrganizationUrl="/dashboard"
          appearance={{
            elements: {
              rootBox: "w-full",
              organizationSwitcherTrigger: "w-full px-4 py-2 border rounded-lg"
            }
          }}
        />
        <p className="text-xs text-gray-500 text-center mt-6">
          Click "Create organization" to get started with Demo Petrol Station
        </p>
      </div>
    </div>
  );
}