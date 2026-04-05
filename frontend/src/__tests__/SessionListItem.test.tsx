import { render, screen, fireEvent } from "@testing-library/react";

import { SessionListItem } from "@/components/chat/SessionListItem";
import type { ChatSession } from "@/components/chat/types";

const session: ChatSession = {
  id: "s1",
  title: "Campaign",
  messages: [],
  createdAt: "2026-04-03T10:00:00.000Z",
  updatedAt: "2026-04-03T10:00:00.000Z",
};

describe("SessionListItem", () => {
  it("renders title and handles click", () => {
    const handleSelect = jest.fn();

    render(
      <SessionListItem
        session={session}
        isActive={false}
        onSelect={handleSelect}
      />
    );

    expect(screen.getByText("Campaign")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button"));
    expect(handleSelect).toHaveBeenCalledWith("s1");
  });
});
