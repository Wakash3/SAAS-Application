"use client";

import { useEffect, useState } from "react";
import { useOrganization, useUser, OrganizationSwitcher } from "@clerk/nextjs";
import { useApi } from "@/lib/api";

export default function DashboardPage() {
  const api = useApi();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const { organization, isLoaded: isOrgLoaded } = useOrganization();
  const { user, isLoaded: isUserLoaded } = useUser();

  useEffect(() => {
    if (!organization) return;
    
    setLoading(true);
    api.get("/api/v1/auth/me")
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [api, organization]);

  if (!isOrgLoaded || !isUserLoaded) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Please sign in</h1>
          <p className="text-gray-600 mb-6">Sign in to access your dashboard</p>
          <a 
            href="/sign-in" 
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Sign In
          </a>
        </div>
      </div>
    );
  }

  if (!organization) {
    return (
      <div className="flex min-h-screen items-center justify-center p-8">
        <div className="text-center max-w-md">
          <h1 className="text-2xl font-bold mb-4">Welcome to Msingi</h1>
          <p className="text-gray-600 mb-6">
            Create an organization to start managing your retail business
          </p>
          <div className="inline-block w-full">
            <OrganizationSwitcher 
              afterCreateOrganizationUrl="/dashboard"
              appearance={{
                elements: {
                  rootBox: "w-full",
                  organizationSwitcherTrigger: "w-full px-4 py-2 border border-gray-300 rounded-lg"
                }
              }}
            />
          </div>
          <p className="mt-6 text-sm text-gray-500">
            💡 Tip: Click "Create organization" to set up your petrol station or retail store
          </p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-8"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="h-32 bg-gray-200 rounded"></div>
            <div className="h-32 bg-gray-200 rounded"></div>
            <div className="h-32 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-2">Dashboard Overview</h1>
      <p className="text-gray-600 mb-6">
        Welcome to <strong>{organization.name}</strong> — your retail intelligence platform.
      </p>
      
      {data && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6 border border-gray-100">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Tenant</h3>
            <p className="text-lg font-semibold">{data.tenant?.name || organization.name}</p>
            <p className="text-sm text-gray-600 mt-1">Plan: {data.tenant?.plan || 'starter'}</p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6 border border-gray-100">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Branches</h3>
            <p className="text-3xl font-bold text-blue-600">{data.branches?.length || 0}</p>
            <p className="text-sm text-gray-600 mt-1">Active locations</p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6 border border-gray-100">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Organization ID</h3>
            <p className="text-sm font-mono text-gray-600 break-all">{organization.id}</p>
          </div>
        </div>
      )}

      {!data && (
        <div className="bg-white rounded-lg shadow p-8 border border-gray-100 text-center">
          <p className="text-gray-600">Loading your business data...</p>
          <p className="text-sm text-gray-400 mt-2">If this takes too long, check your database connection</p>
        </div>
      )}

      <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-100">
        <p className="text-sm text-blue-700">
          💡 Ask Gladwell (bottom right) about today's sales, stock levels, or fuel status.
        </p>
      </div>
    </div>
  );
}