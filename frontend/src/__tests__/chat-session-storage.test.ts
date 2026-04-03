import type { ChatSession } from "@/components/chat/types";
import {
  loadSessionSnapshot,
  persistSessionSnapshot,
} from "@/lib/chat-session-storage";

const sessionFixture: ChatSession = {
  id: "session-1",
  title: "Test session",
  messages: [],
  createdAt: "2026-04-03T10:00:00.000Z",
  updatedAt: "2026-04-03T10:00:00.000Z",
};

describe("chat-session-storage", () => {
  const warnSpy = jest.spyOn(console, "warn").mockImplementation(() => undefined);

  beforeEach(() => {
    window.localStorage.clear();
  });

  afterAll(() => {
    warnSpy.mockRestore();
  });

  it("returns empty snapshot when storage is empty", () => {
    const snapshot = loadSessionSnapshot();

    expect(snapshot.sessions).toEqual([]);
    expect(snapshot.activeSessionId).toBeNull();
  });

  it("persists and loads sessions", () => {
    persistSessionSnapshot({
      sessions: [sessionFixture],
      activeSessionId: sessionFixture.id,
    });

    const snapshot = loadSessionSnapshot();

    expect(snapshot.sessions).toHaveLength(1);
    expect(snapshot.sessions[0].id).toBe("session-1");
    expect(snapshot.activeSessionId).toBe("session-1");
  });

  it("handles malformed data gracefully", () => {
    window.localStorage.setItem("julius-caesair.sessions.v1", "not-json");

    const snapshot = loadSessionSnapshot();

    expect(snapshot.sessions).toEqual([]);
    expect(warnSpy).toHaveBeenCalled();
  });
});
