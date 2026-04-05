import { render, screen } from "@testing-library/react";

import { TypingIndicator } from "@/components/chat/TypingIndicator";

describe("TypingIndicator", () => {
  it("renders three dots", () => {
    render(<TypingIndicator />);

    expect(screen.getByTestId("typing-indicator")).toBeInTheDocument();
  });
});
