import { NextResponse } from "next/server";

const backendBaseUrl =
  process.env.BACKEND_BASE_URL ?? "http://127.0.0.1:5000";

export async function POST(request: Request) {
  try {
    const body = await request.json();

    const response = await fetch(`${backendBaseUrl}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      cache: "no-store",
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
