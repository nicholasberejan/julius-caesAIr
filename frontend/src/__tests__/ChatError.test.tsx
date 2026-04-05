import { render, screen } from "@testing-library/react";

import { ChatError } from "@/components/chat/ChatError";

describe("ChatError", () => {
  it("renders nothing when message is null", () => {
    const { container } = render(<ChatError message={null} />);

    expect(container).toBeEmptyDOMElement();
  });

  it("renders message when provided", () => {
    render(<ChatError message="Something went wrong" />);

    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
  });
});
