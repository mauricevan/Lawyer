export type QueryMode = "open" | "compliance" | "compare" | "updates";
export type Audience = "layperson" | "professional";

export interface TrustIndicator {
  is_consolidated: boolean;
  is_in_force: boolean;
  last_modified?: string;
  oj_reference?: string;
  has_corrigendum: boolean;
  corrigendum_celex?: string;
  has_amendment?: boolean;
}

export interface Citation {
  celex: string;
  article?: string;
  title?: string;
  excerpt: string;
  eli_uri?: string;
  eurlex_url: string;
  trust: TrustIndicator;
  legal_citation: string;
}

export interface AnswerResponse {
  answer: string;
  conversation_id: string;
  citations: Citation[];
  disclaimer: string;
}

export interface QueryRequest {
  question: string;
  conversation_id?: string;
  query_mode: QueryMode;
  audience?: Audience;
  language?: string;
}

export interface Message {
  id: string;
  role: string;
  content: string;
  citations: Citation[];
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  query_mode: string;
  is_saved: boolean;
  messages: Message[];
}

export interface RetrievalEvent {
  step: string;
  message: string;
  detail?: Record<string, unknown>;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  isPending?: boolean;
}
