export type QueryMode = "open" | "compliance" | "compare" | "updates";
export type Audience = "layperson" | "professional";
export type SupportedLanguage = "auto" | "nl" | "en" | "fr" | "de" | "es";
export type RetrievalRoute = "local" | "live_fallback" | "hybrid" | "cache";

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
  retrieval_score?: number;
  rerank_score?: number;
}

export interface RetrievalExplainability {
  route: RetrievalRoute;
  query_language: string;
  router: {
    domains: string[];
    doc_types: string[];
    celex_hint?: string;
    language: string;
    time_context?: "current" | "historical";
    intent_id?: string;
    confidence?: number;
    domain_cluster?: string;
  };
  reranker_variant: string;
  rerank_latency_ms: number;
  hybrid_rrf_enabled: boolean;
  stage_counts: Record<string, number>;
  sources: Array<{
    chunk_id: string;
    celex: string;
    vector_score?: number;
    rerank_score?: number;
  }>;
}

export interface AnswerResponse {
  answer: string;
  conversation_id: string;
  citations: Citation[];
  disclaimer: string;
  retrieval_route?: RetrievalRoute;
  confidence_score?: number;
  verification_questions?: string[];
  retrieval_explainability?: RetrievalExplainability;
}

export interface QueryRequest {
  question: string;
  conversation_id?: string;
  query_mode: QueryMode;
  audience?: Audience;
  language?: SupportedLanguage;
  filters?: {
    domain?: string;
    doc_type?: string;
    celex?: string;
    language?: SupportedLanguage;
    time_context?: "current" | "historical";
    in_force_only?: boolean;
    consolidated_preferred?: boolean;
  };
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
  verificationQuestions?: string[];
  isPending?: boolean;
}

export type FeedbackCategory = "incorrect" | "incomplete" | "source_issue" | "ux" | "positive";

export interface FeedbackRequest {
  rating: number;
  category?: FeedbackCategory;
  comment?: string;
  conversation_id?: string;
}
