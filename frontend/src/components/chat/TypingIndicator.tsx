export function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 text-zinc-500" data-testid="typing-indicator">
      <span className="h-2 w-2 animate-pulse rounded-full bg-zinc-400" />
      <span className="h-2 w-2 animate-pulse rounded-full bg-zinc-400 [animation-delay:150ms]" />
      <span className="h-2 w-2 animate-pulse rounded-full bg-zinc-400 [animation-delay:300ms]" />
    </div>
  );
}
