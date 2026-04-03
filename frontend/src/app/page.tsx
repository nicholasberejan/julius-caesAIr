"use client";

import { useState } from "react";

import { ChatError } from "@/components/chat/ChatError";
import { ChatHeader } from "@/components/chat/ChatHeader";
import { ChatInput } from "@/components/chat/ChatInput";
import { ChatMessages } from "@/components/chat/ChatMessages";
import type { ChatMessage, ChatResponse } from "@/components/chat/types";

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

    const assistantId = crypto.randomUUID();
    setMessages((prev) => [
      ...prev,
      { id: assistantId, role: "assistant", content: "", isStreaming: true },
    ]);

    try {
      const response = await fetch("/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed }),
      });

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      if (!response.body) {
        const payload = (await response.json()) as ChatResponse;
        setMessages((prev) =>
          prev.map((message) =>
            message.id === assistantId
              ? {
                  ...message,
                  content: payload.answer,
                  sources: payload.sources,
                  isStreaming: false,
                }
              : message
          )
        );
        return;
      }

      // `response.body` is a ReadableStream from the Fetch API.
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      const updateAssistant = (delta: string) => {
        setMessages((prev) =>
          prev.map((message) =>
            message.id === assistantId
              ? { ...message, content: message.content + delta }
              : message
          )
        );
      };

      while (true) {
        const { value, done } = await reader.read();
        if (done) {
          break;
        }
        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        buffer = parts.pop() ?? "";

        for (const part of parts) {
          const line = part
            .split("\n")
            .find((entry) => entry.startsWith("data: "));
          if (!line) {
            continue;
          }
          const payload = JSON.parse(line.replace("data: ", ""));
            if (payload.delta) {
              updateAssistant(payload.delta);
            } else if (payload.done) {
              setMessages((prev) =>
                prev.map((message) =>
                  message.id === assistantId
                    ? {
                        ...message,
                        content: payload.answer ?? message.content,
                        sources: payload.sources ?? message.sources,
                        isStreaming: false,
                      }
                    : message
                )
              );
            } else if (payload.error) {
            throw new Error(payload.message ?? "Streaming error");
          }
        }
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setError(message);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantId ? { ...msg, isStreaming: false } : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-50 text-zinc-900">
      <main className="mx-auto flex w-full max-w-4xl flex-col gap-6 px-6 py-10">
        <ChatHeader />

        <section className="flex flex-1 flex-col gap-4 rounded-xl border border-zinc-200 bg-white p-4 shadow-sm">
          <div className="flex flex-1 flex-col gap-4 overflow-y-auto">
            <ChatMessages messages={messages} />
          </div>

          <ChatError message={error} />

          <ChatInput
            value={input}
            isLoading={isLoading}
            onChange={setInput}
            onSend={sendMessage}
          />
        </section>
      </main>
    </div>
  );
}
