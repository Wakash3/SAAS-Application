import Link from "next/link";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-green-700 mb-4">Msingi</h1>
        <p className="text-gray-600 mb-8">Retail Intelligence Platform</p>
        <div className="space-y-4">
          <Link href="/sign-up">
            <button className="w-48 px-6 py-3 bg-green-700 text-white rounded-lg hover:bg-green-800">
              Sign Up
            </button>
          </Link>
          <br />
          <Link href="/sign-in">
            <button className="w-48 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">
              Sign In
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
}
