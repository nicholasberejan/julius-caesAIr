import type { ChatSession } from "@/components/chat/types";
import { formatShortDate } from "@/lib/date-format";
import { DEFAULT_SESSION_TITLE } from "@/lib/chat-session-utils";

const baseClassName =
  "w-full rounded-md border px-3 py-2 text-left text-sm transition-colors";
const activeClassName =
  "border-zinc-900 bg-zinc-900 text-white";
const inactiveClassName =
  "border-transparent text-zinc-700 hover:border-zinc-200 hover:bg-zinc-50";

const timestampClassName = {
  active: "mt-1 text-xs text-zinc-200",
  inactive: "mt-1 text-xs text-zinc-400",
};

type SessionListItemProps = {
  session: ChatSession;
  isActive: boolean;
  onSelect: (sessionId: string) => void;
};

export function SessionListItem({
  session,
  isActive,
  onSelect,
}: SessionListItemProps) {
  return (
    <button
      type="button"
      onClick={() => onSelect(session.id)}
      className={`${baseClassName} ${
        isActive ? activeClassName : inactiveClassName
      }`}
    >
      <div className="line-clamp-2 font-medium">
        {session.title || DEFAULT_SESSION_TITLE}
      </div>
      <div className={isActive ? timestampClassName.active : timestampClassName.inactive}>
        {formatShortDate(session.updatedAt)}
      </div>
    </button>
  );
}
