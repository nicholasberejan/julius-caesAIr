"use client";

import { useEffect, useMemo, useState } from "react";

import { ChatError } from "@/components/chat/ChatError";
import { ChatHeader } from "@/components/chat/ChatHeader";
import { ChatInput } from "@/components/chat/ChatInput";
import { ChatMessages } from "@/components/chat/ChatMessages";
import { SessionSidebar } from "@/components/chat/SessionSidebar";
import type { ChatMessage, ChatResponse, ChatSession } from "@/components/chat/types";
import {
  loadSessionSnapshot,
  persistSessionSnapshot,
} from "@/lib/chat-session-storage";
import {
  appendMessage,
  createSession,
  sortSessionsByUpdatedAt,
  updateAssistantMessage as updateAssistantMessageInSession,
} from "@/lib/chat-session-utils";

export default function Home() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isHydrated, setIsHydrated] = useState(false);

  const activeSession = useMemo(
    () => sessions.find((session) => session.id === activeSessionId) ?? null,
    [sessions, activeSessionId]
  );
  const messages = activeSession?.messages ?? [];

  useEffect(() => {
    const snapshot = loadSessionSnapshot();
    if (snapshot.sessions.length > 0) {
      setSessions(snapshot.sessions);
      setActiveSessionId(
        snapshot.activeSessionId ?? snapshot.sessions[0]?.id ?? null
      );
    } else {
      const newSession = createSession();
      setSessions([newSession]);
      setActiveSessionId(newSession.id);
    }
    setIsHydrated(true);
  }, []);

  useEffect(() => {
    if (!isHydrated) {
      return;
    }
    persistSessionSnapshot({
      sessions,
      activeSessionId,
    });
  }, [sessions, activeSessionId, isHydrated]);

  const handleNewChat = () => {
    const newSession = createSession();
    setSessions((prev) => [newSession, ...prev]);
    setActiveSessionId(newSession.id);
    setError(null);
    setInput("");
  };

  const updateSessionById = (
    sessionId: string | null,
    updater: (session: ChatSession) => ChatSession
  ) => {
    if (!sessionId) {
      return;
    }
    setSessions((prev) =>
      prev.map((session) =>
        session.id === sessionId ? updater(session) : session
      )
    );
  };

  const ensureActiveSession = () => {
    if (activeSessionId) {
      return activeSessionId;
    }
    const newSession = createSession();
    setSessions((prev) => [newSession, ...prev]);
    setActiveSessionId(newSession.id);
    return newSession.id;
  };

  const appendMessageToSession = (sessionId: string, message: ChatMessage) => {
    updateSessionById(sessionId, (session) => appendMessage(session, message));
  };

  const updateAssistantMessage = (
    sessionId: string,
    assistantId: string,
    updater: (message: ChatMessage) => ChatMessage
  ) => {
    updateSessionById(sessionId, (session) =>
      updateAssistantMessageInSession(session, assistantId, updater)
    );
  };

  const sendMessage = async () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) {
      return;
    }

    setError(null);
    setIsLoading(true);
    const sessionId = ensureActiveSession();

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmed,
    };

    appendMessageToSession(sessionId, userMessage);
    setInput("");

    const assistantId = crypto.randomUUID();
    appendMessageToSession(sessionId, {
      id: assistantId,
      role: "assistant",
      content: "",
      isStreaming: true,
    });

    try {
      const response = await fetch("/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed, session_id: sessionId }),
      });

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      if (!response.body) {
        const payload = (await response.json()) as ChatResponse;
        updateAssistantMessage(sessionId, assistantId, (message) => ({
          ...message,
          content: payload.answer,
          sources: payload.sources,
          isStreaming: false,
        }));
        return;
      }

      // `response.body` is a ReadableStream from the Fetch API.
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      const updateAssistant = (delta: string) => {
        updateAssistantMessage(sessionId, assistantId, (message) => ({
          ...message,
          content: message.content + delta,
        }));
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
              updateAssistantMessage(sessionId, assistantId, (message) => ({
                ...message,
                content: payload.answer ?? message.content,
                sources: payload.sources ?? message.sources,
                isStreaming: false,
              }));
            } else if (payload.error) {
              throw new Error(payload.message ?? "Streaming error");
            }
        }
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setError(message);
      updateAssistantMessage(sessionId, assistantId, (msg) => ({
        ...msg,
        isStreaming: false,
      }));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen gap-6 bg-zinc-50 text-zinc-900">
      <SessionSidebar
        sessions={sortSessionsByUpdatedAt(sessions)}
        activeSessionId={activeSessionId}
        onSelect={setActiveSessionId}
        onNew={handleNewChat}
      />
      <main className="flex h-screen flex-1 flex-col gap-6 px-6 py-10">
        <ChatHeader title={activeSession?.title} />

        <section className="flex flex-1 min-h-0 flex-col gap-4 rounded-xl border border-zinc-200 bg-white p-4 shadow-sm">
          <div className="flex flex-1 flex-col gap-4 overflow-y-auto">
            <ChatMessages messages={messages} />
          </div>

          <ChatError message={error} />

          <div className="sticky bottom-0 bg-white pt-2">
            <ChatInput
              value={input}
              isLoading={isLoading}
              onChange={setInput}
              onSend={sendMessage}
            />
          </div>
        </section>
      </main>
    </div>
  );
}
