import { render, screen } from "@testing-library/react";

import { ChatMessageCard } from "@/components/chat/ChatMessageCard";
import type { ChatMessage } from "@/components/chat/types";

describe("ChatMessageCard", () => {
  it("shows typing indicator when streaming and empty", () => {
    const message: ChatMessage = {
      id: "a1",
      role: "assistant",
      content: "",
      isStreaming: true,
    };

    render(<ChatMessageCard message={message} />);

    expect(screen.getByTestId("typing-indicator")).toBeInTheDocument();
  });

  it("renders message content", () => {
    const message: ChatMessage = {
      id: "u1",
      role: "user",
      content: "Hello Caesar",
    };

    render(<ChatMessageCard message={message} />);

    expect(screen.getByText("Hello Caesar")).toBeInTheDocument();
  });
});
