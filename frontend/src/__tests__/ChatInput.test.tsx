import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ChatInput } from "@/components/chat/ChatInput";

describe("ChatInput", () => {
  it("calls onSend when clicking send", async () => {
    const user = userEvent.setup();
    const handleSend = jest.fn();

    render(
      <ChatInput
        value="Hello"
        isLoading={false}
        onChange={() => undefined}
        onSend={handleSend}
      />
    );

    await user.click(screen.getByRole("button", { name: "Send" }));
    expect(handleSend).toHaveBeenCalledTimes(1);
  });

  it("calls onSend when pressing Enter", async () => {
    const user = userEvent.setup();
    const handleSend = jest.fn();

    render(
      <ChatInput
        value="Hello"
        isLoading={false}
        onChange={() => undefined}
        onSend={handleSend}
      />
    );

    const textbox = screen.getByRole("textbox");
    await user.type(textbox, "{enter}");

    expect(handleSend).toHaveBeenCalledTimes(1);
  });
});
