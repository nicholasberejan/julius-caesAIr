import type { ChatMessage, ChatSession } from "@/components/chat/types";
import {
  DEFAULT_SESSION_TITLE,
  appendMessage,
  createSession,
  deriveSessionTitle,
  sortSessionsByUpdatedAt,
} from "@/lib/chat-session-utils";

describe("chat-session-utils", () => {
  it("creates a new session with defaults", () => {
    const now = new Date("2026-04-03T10:00:00.000Z");
    const session = createSession(now);

    expect(session.title).toBe(DEFAULT_SESSION_TITLE);
    expect(session.messages).toEqual([]);
    expect(session.createdAt).toBe(now.toISOString());
  });

  it("derives a title from first user message", () => {
    const message: ChatMessage = {
      id: "m1",
      role: "user",
      content: "Tell me about the Belgae",
    };

    const title = deriveSessionTitle(DEFAULT_SESSION_TITLE, message);

    expect(title).toContain("Tell me about the Belgae");
  });

  it("does not change title once set", () => {
    const message: ChatMessage = {
      id: "m1",
      role: "user",
      content: "New question",
    };

    const title = deriveSessionTitle("Existing title", message);

    expect(title).toBe("Existing title");
  });

  it("appends messages and updates timestamp", () => {
    const baseSession: ChatSession = {
      id: "s1",
      title: DEFAULT_SESSION_TITLE,
      messages: [],
      createdAt: "2026-04-03T10:00:00.000Z",
      updatedAt: "2026-04-03T10:00:00.000Z",
    };
    const message: ChatMessage = {
      id: "m1",
      role: "user",
      content: "Hello",
    };
    const now = new Date("2026-04-03T12:00:00.000Z");

    const next = appendMessage(baseSession, message, now);

    expect(next.messages).toHaveLength(1);
    expect(next.updatedAt).toBe(now.toISOString());
  });

  it("sorts sessions by updatedAt desc", () => {
    const sessions: ChatSession[] = [
      {
        id: "a",
        title: "A",
        messages: [],
        createdAt: "2026-04-03T10:00:00.000Z",
        updatedAt: "2026-04-03T10:00:00.000Z",
      },
      {
        id: "b",
        title: "B",
        messages: [],
        createdAt: "2026-04-03T10:00:00.000Z",
        updatedAt: "2026-04-04T10:00:00.000Z",
      },
    ];

    const sorted = sortSessionsByUpdatedAt(sessions);

    expect(sorted[0].id).toBe("b");
    expect(sorted[1].id).toBe("a");
  });
});
