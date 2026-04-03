import { Button } from "@/components/ui/button";
import type { ChatSession } from "@/components/chat/types";

const formatTimestamp = (timestamp: string) => {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  return date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });
};

type SessionSidebarProps = {
  sessions: ChatSession[];
  activeSessionId: string | null;
  onSelect: (sessionId: string) => void;
  onNew: () => void;
};

export function SessionSidebar({
  sessions,
  activeSessionId,
  onSelect,
  onNew,
}: SessionSidebarProps) {
  return (
    <aside className="flex h-screen w-64 flex-col gap-4 border-r border-zinc-200 bg-white py-4 pl-6 pr-4">
      <Button onClick={onNew} className="w-full">
        New chat
      </Button>
      <div className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
        Sessions
      </div>
      <div className="flex-1 space-y-2 overflow-y-auto">
        {sessions.length === 0 ? (
          <div className="text-sm text-zinc-500">No sessions yet.</div>
        ) : (
          sessions.map((session) => {
            const isActive = session.id === activeSessionId;
            return (
              <button
                key={session.id}
                type="button"
                onClick={() => onSelect(session.id)}
                className={
                  isActive
                    ? "w-full rounded-md border border-zinc-900 bg-zinc-900 px-3 py-2 text-left text-sm text-white"
                    : "w-full rounded-md border border-transparent px-3 py-2 text-left text-sm text-zinc-700 hover:border-zinc-200 hover:bg-zinc-50"
                }
              >
                <div className="line-clamp-2 font-medium">
                  {session.title || "New chat"}
                </div>
                <div
                  className={
                    isActive
                      ? "mt-1 text-xs text-zinc-200"
                      : "mt-1 text-xs text-zinc-400"
                  }
                >
                  {formatTimestamp(session.updatedAt)}
                </div>
              </button>
            );
          })
        )}
      </div>
    </aside>
  );
}
