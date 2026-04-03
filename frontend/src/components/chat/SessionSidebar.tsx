import type { ChatSession } from "@/components/chat/types";
import { SessionListItem } from "@/components/chat/SessionListItem";
import { Button } from "@/components/ui/button";

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
          sessions.map((session) => (
            <SessionListItem
              key={session.id}
              session={session}
              isActive={session.id === activeSessionId}
              onSelect={onSelect}
            />
          ))
        )}
      </div>
    </aside>
  );
}
