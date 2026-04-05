import type { ChatSession } from "@/components/chat/types";

const SESSIONS_KEY = "julius-caesair.sessions.v1";
const ACTIVE_SESSION_KEY = "julius-caesair.active-session.v1";

export type SessionStorageSnapshot = {
  sessions: ChatSession[];
  activeSessionId: string | null;
};

export function loadSessionSnapshot(): SessionStorageSnapshot {
  if (typeof window === "undefined") {
    return { sessions: [], activeSessionId: null };
  }

  try {
    const rawSessions = window.localStorage.getItem(SESSIONS_KEY);
    const rawActive = window.localStorage.getItem(ACTIVE_SESSION_KEY);
    const sessions = rawSessions ? (JSON.parse(rawSessions) as ChatSession[]) : [];
    return {
      sessions: Array.isArray(sessions) ? sessions : [],
      activeSessionId: rawActive || null,
    };
  } catch (error) {
    console.warn("Failed to load chat sessions", error);
    return { sessions: [], activeSessionId: null };
  }
}

export function persistSessionSnapshot(snapshot: SessionStorageSnapshot) {
  if (typeof window === "undefined") {
    return;
  }

  try {
    window.localStorage.setItem(SESSIONS_KEY, JSON.stringify(snapshot.sessions));
    if (snapshot.activeSessionId) {
      window.localStorage.setItem(ACTIVE_SESSION_KEY, snapshot.activeSessionId);
    } else {
      window.localStorage.removeItem(ACTIVE_SESSION_KEY);
    }
  } catch (error) {
    console.warn("Failed to persist chat sessions", error);
  }
}
