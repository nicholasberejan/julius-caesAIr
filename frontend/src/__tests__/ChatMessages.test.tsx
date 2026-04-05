import { render, screen } from "@testing-library/react";

import { ChatMessages } from "@/components/chat/ChatMessages";
import type { ChatMessage } from "@/components/chat/types";

describe("ChatMessages", () => {
  it("renders empty state when no messages", () => {
    render(<ChatMessages messages={[]} />);

    expect(
      screen.getByText(/No messages yet/i)
    ).toBeInTheDocument();
  });

  it("renders list of messages", () => {
    const messages: ChatMessage[] = [
      { id: "m1", role: "user", content: "Hello" },
      { id: "m2", role: "assistant", content: "Ave" },
    ];

    render(<ChatMessages messages={messages} />);

    expect(screen.getByText("Hello")).toBeInTheDocument();
    expect(screen.getByText("Ave")).toBeInTheDocument();
  });
});
