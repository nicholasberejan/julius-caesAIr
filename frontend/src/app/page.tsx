"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

type ChatSource = {
  source: string;
  page?: number | null;
  excerpt: string;
  score?: number | null;
};

type ChatResponse = {
  answer: string;
  question: string;
  status: string;
  sources: ChatSource[];
  classifier?: {
    allowed: boolean;
    reason: string;
  } | null;
};

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: ChatSource[];
};

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = async () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) {
      return;
    }

    setError(null);
    setIsLoading(true);

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmed,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed }),
      });

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const payload = (await response.json()) as ChatResponse;
      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: payload.answer,
        sources: payload.sources ?? [],
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-50 text-zinc-900">
      <main className="mx-auto flex w-full max-w-4xl flex-col gap-6 px-6 py-10">
        <header className="space-y-2">
          <h1 className="text-3xl font-semibold tracking-tight">
            julius-caesAIr
          </h1>
          <p className="text-sm text-zinc-600">
            Ask Caesar a question grounded in his writings.
          </p>
        </header>

        <section className="flex flex-1 flex-col gap-4 rounded-xl border border-zinc-200 bg-white p-4 shadow-sm">
          <div className="flex flex-1 flex-col gap-4 overflow-y-auto">
            {messages.length === 0 ? (
              <div className="text-sm text-zinc-500">
                No messages yet. Ask about the Helvetii, Gauls, or Caesar&apos;s
                campaigns.
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={
                    message.role === "user"
                      ? "self-end rounded-lg bg-zinc-900 px-4 py-3 text-sm text-white"
                      : "self-start rounded-lg border border-zinc-200 bg-zinc-50 px-4 py-3 text-sm text-zinc-900"
                  }
                >
                  <p className="whitespace-pre-wrap leading-relaxed">
                    {message.content}
                  </p>
                  {message.role === "assistant" &&
                  message.sources &&
                  message.sources.length > 0 ? (
                    <div className="mt-3 text-xs text-zinc-600">
                      <div className="font-semibold">Sources</div>
                      <ul className="mt-1 space-y-2">
                        {message.sources.map((source, index) => (
                          <li key={`${source.source}-${index}`}>
                            <div className="font-medium">
                              {source.source}
                              {source.page ? ` (page ${source.page})` : ""}
                            </div>
                            <div className="mt-1 italic">
                              {source.excerpt}
                            </div>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ) : null}
                </div>
              ))
            )}
          </div>

          {error ? (
            <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </div>
          ) : null}

          <div className="flex flex-col gap-3">
            <Textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask Julius Caesar about his campaigns, politics, or rivals..."
              rows={3}
              className="resize-none"
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  void sendMessage();
                }
              }}
            />
            <div className="flex items-center justify-between">
              <div className="text-xs text-zinc-500">
                {isLoading ? "Caesar is responding..." : ""}
              </div>
              <Button onClick={sendMessage} disabled={isLoading}>
                Send
              </Button>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
