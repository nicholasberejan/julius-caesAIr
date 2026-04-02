import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

type ChatInputProps = {
  value: string;
  isLoading: boolean;
  onChange: (value: string) => void;
  onSend: () => void;
};

export function ChatInput({ value, isLoading, onChange, onSend }: ChatInputProps) {
  return (
    <div className="flex flex-col gap-3">
      <Textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Ask Julius Caesar about his campaigns, politics, or rivals..."
        rows={3}
        className="resize-none"
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            onSend();
          }
        }}
      />
      <div className="flex items-center justify-between">
        <div className="text-xs text-zinc-500">
          {isLoading ? "Caesar is responding..." : ""}
        </div>
        <Button onClick={onSend} disabled={isLoading}>
          Send
        </Button>
      </div>
    </div>
  );
}
