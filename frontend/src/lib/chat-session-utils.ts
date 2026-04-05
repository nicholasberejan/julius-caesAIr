import type { ChatMessage, ChatSession } from "@/components/chat/types";

export const DEFAULT_SESSION_TITLE = "New chat";

export const createSession = (now = new Date()): ChatSession => {
  const timestamp = now.toISOString();
  return {
    id: crypto.randomUUID(),
    title: DEFAULT_SESSION_TITLE,
    messages: [],
    createdAt: timestamp,
    updatedAt: timestamp,
  };
};

export const deriveSessionTitle = (
  currentTitle: string,
  message: ChatMessage
): string => {
  if (currentTitle !== DEFAULT_SESSION_TITLE) {
    return currentTitle;
  }
  if (message.role !== "user") {
    return currentTitle;
  }
  return message.content.slice(0, 48) || DEFAULT_SESSION_TITLE;
};

export const appendMessage = (
  session: ChatSession,
  message: ChatMessage,
  now = new Date()
): ChatSession => {
  return {
    ...session,
    title: deriveSessionTitle(session.title, message),
    messages: [...session.messages, message],
    updatedAt: now.toISOString(),
  };
};

export const updateAssistantMessage = (
  session: ChatSession,
  assistantId: string,
  updater: (message: ChatMessage) => ChatMessage,
  now = new Date()
): ChatSession => {
  return {
    ...session,
    messages: session.messages.map((message) =>
      message.id === assistantId ? updater(message) : message
    ),
    updatedAt: now.toISOString(),
  };
};

export const sortSessionsByUpdatedAt = (
  sessions: ChatSession[]
): ChatSession[] => {
  return [...sessions].sort(
    (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
  );
};
