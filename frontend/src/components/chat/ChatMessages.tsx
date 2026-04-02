import type { ChatMessage } from "@/components/chat/types";
import { ChatMessageCard } from "@/components/chat/ChatMessageCard";

type ChatMessagesProps = {
  messages: ChatMessage[];
};

export function ChatMessages({ messages }: ChatMessagesProps) {
  if (messages.length === 0) {
    return (
      <div className="text-sm text-zinc-500">
        No messages yet. Ask about the Helvetii, Gauls, or Caesar&apos;s campaigns.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      {messages.map((message) => (
        <ChatMessageCard key={message.id} message={message} />
      ))}
    </div>
  );
}
