import { render, screen, fireEvent } from "@testing-library/react";

import { SessionSidebar } from "@/components/chat/SessionSidebar";
import type { ChatSession } from "@/components/chat/types";

const sessions: ChatSession[] = [
  {
    id: "s1",
    title: "First session",
    messages: [],
    createdAt: "2026-04-03T10:00:00.000Z",
    updatedAt: "2026-04-03T10:00:00.000Z",
  },
  {
    id: "s2",
    title: "Second session",
    messages: [],
    createdAt: "2026-04-03T11:00:00.000Z",
    updatedAt: "2026-04-03T11:00:00.000Z",
  },
];

describe("SessionSidebar", () => {
  it("renders sessions and handles selection", () => {
    const handleSelect = jest.fn();
    const handleNew = jest.fn();

    render(
      <SessionSidebar
        sessions={sessions}
        activeSessionId="s1"
        onSelect={handleSelect}
        onNew={handleNew}
      />
    );

    expect(screen.getByText("Sessions")).toBeInTheDocument();
    expect(screen.getByText("First session")).toBeInTheDocument();
    expect(screen.getByText("Second session")).toBeInTheDocument();

    fireEvent.click(screen.getByText("Second session"));
    expect(handleSelect).toHaveBeenCalledWith("s2");

    fireEvent.click(screen.getByRole("button", { name: "New chat" }));
    expect(handleNew).toHaveBeenCalledTimes(1);
  });

  it("renders empty state when no sessions", () => {
    render(
      <SessionSidebar
        sessions={[]}
        activeSessionId={null}
        onSelect={() => undefined}
        onNew={() => undefined}
      />
    );

    expect(screen.getByText("No sessions yet.")).toBeInTheDocument();
  });
});
