export type ChatSource = {
  source: string;
  page?: number | null;
  excerpt: string;
  score?: number | null;
};

export type ChatResponse = {
  answer: string;
  question: string;
  status: string;
  sources: ChatSource[];
  classifier?: {
    allowed: boolean;
    reason: string;
  } | null;
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: ChatSource[];
  isStreaming?: boolean;
};

export type ChatSession = {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: string;
  updatedAt: string;
};
