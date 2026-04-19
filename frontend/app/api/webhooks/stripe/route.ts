import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const body = await req.text();
  const sig = req.headers.get("stripe-signature") || "";
  await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/webhooks/stripe`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "stripe-signature": sig },
    body,
  });
  return NextResponse.json({ received: true });
}