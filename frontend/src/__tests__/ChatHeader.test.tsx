import { render, screen } from "@testing-library/react";

import { ChatHeader } from "@/components/chat/ChatHeader";

describe("ChatHeader", () => {
  it("renders app title", () => {
    render(<ChatHeader />);

    expect(screen.getByText("julius-caesAIr")).toBeInTheDocument();
  });

  it("renders session title when provided", () => {
    render(<ChatHeader title="Campaign Notes" />);

    expect(screen.getByText("Campaign Notes")).toBeInTheDocument();
  });
});
