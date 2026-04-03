type ChatHeaderProps = {
  title?: string;
};

export function ChatHeader({ title }: ChatHeaderProps) {
  return (
    <header className="space-y-2">
      <div className="flex items-baseline justify-between gap-4">
        <h1 className="text-3xl font-semibold tracking-tight">julius-caesAIr</h1>
        {title ? (
          <div className="text-sm font-medium text-zinc-500">{title}</div>
        ) : null}
      </div>
      <p className="text-sm text-zinc-600">
        Ask Caesar a question grounded in his writings.
      </p>
    </header>
  );
}
