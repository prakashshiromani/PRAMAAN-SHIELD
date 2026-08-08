import { NextRequest, NextResponse } from "next/server";
import { API_BASE_URL } from "@/lib/api";

export const runtime = "nodejs";

/**
 * Server-only proxy for PRAMAAN Seal issuance (audit Issue 03).
 *
 * The issuer API key (SEAL_API_KEY) lives exclusively in this route handler /
 * server env. It is never exposed via NEXT_PUBLIC_* and never reaches the
 * browser bundle — a public issuer key would let anyone mint regulatory seals.
 */
export async function POST(request: NextRequest) {
  const apiKey = process.env.SEAL_API_KEY || "demo_seal_api_key";
  const backend = API_BASE_URL;

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json(
      { error: true, detail: "Invalid JSON body." },
      { status: 400 },
    );
  }

  try {
    const res = await fetch(`${backend}/api/seal/sign`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": apiKey,
      },
      body: JSON.stringify(body),
    });

    const data = await res.json().catch(() => ({}));
    return NextResponse.json(data, { status: res.status });
  } catch {
    return NextResponse.json(
      { error: true, detail: "Backend seal service unreachable." },
      { status: 502 },
    );
  }
}
