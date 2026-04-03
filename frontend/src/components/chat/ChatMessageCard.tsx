import type { ChatMessage } from "@/components/chat/types";
import { TypingIndicator } from "@/components/chat/TypingIndicator";

type ChatMessageCardProps = {
  message: ChatMessage;
};

export function ChatMessageCard({ message }: ChatMessageCardProps) {
  const showTypingIndicator =
    message.role === "assistant" &&
    message.isStreaming &&
    message.content.trim().length === 0;

  return (
    <div
      className={
        message.role === "user"
          ? "self-end rounded-lg bg-zinc-900 px-4 py-3 text-sm text-white"
          : "self-start rounded-lg border border-zinc-200 bg-zinc-50 px-4 py-3 text-sm text-zinc-900"
      }
    >
      {showTypingIndicator ? (
        <TypingIndicator />
      ) : (
        <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
      )}
      {message.role === "assistant" &&
      message.sources &&
      message.sources.length > 0 ? (
        <div className="mt-3 text-xs text-zinc-600">
          <div className="font-semibold">Sources</div>
          <ul className="mt-1 space-y-2">
            {message.sources.map((source, index) => (
              <li key={`${source.source}-${index}`}>
                <div className="font-medium">
                  {source.source}
                  {source.page ? ` (page ${source.page})` : ""}
                  {typeof source.score === "number"
                    ? ` • score ${source.score.toFixed(3)}`
                    : ""}
                </div>
                <div className="mt-1 italic">{source.excerpt}</div>
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
