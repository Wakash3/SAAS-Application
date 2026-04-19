import { NextRequest, NextResponse } from "next/server";

// M-Pesa callbacks come to the backend directly (Railway URL).
// This frontend route is only needed if you route via Vercel.
export async function POST(req: NextRequest) {
  const body = await req.json();
  // Forward to backend
  await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/payments/mpesa/callback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return NextResponse.json({ ResultCode: 0, ResultDesc: "Accepted" });
}