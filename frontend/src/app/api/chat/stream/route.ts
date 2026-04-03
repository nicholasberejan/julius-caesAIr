import { NextResponse } from "next/server";

const backendBaseUrl =
  process.env.BACKEND_BASE_URL ?? "http://127.0.0.1:5000";

export async function POST(request: Request) {
  try {
    const body = await request.json();

    const response = await fetch(`${backendBaseUrl}/api/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      cache: "no-store",
    });

    if (!response.body) {
      return NextResponse.json(
        { error: "Backend stream unavailable." },
        { status: 502 }
      );
    }

    return new Response(response.body, {
      status: response.status,
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
