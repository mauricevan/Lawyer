import type {
  AnswerResponse,
  Audience,
  Citation,
  Conversation,
  QueryMode,
  QueryRequest,
  RetrievalEvent,
} from "@/models/types";
import { getDisclaimer } from "@/content/legalDisclaimers";

export { getDisclaimer };

export function normalizeCitation(citation: Partial<Citation> & { celex: string }): Citation {
  return {
    celex: citation.celex,
    article: citation.article,
    title: citation.title,
    excerpt: citation.excerpt || "",
    eli_uri: citation.eli_uri,
    eurlex_url:
      citation.eurlex_url ||
      `https://eur-lex.europa.eu/legal-content/NL/TXT/?uri=CELEX:${citation.celex}`,
    legal_citation: citation.legal_citation || "",
    trust: citation.trust || {
      is_consolidated: false,
      is_in_force: true,
      has_corrigendum: false,
    },
  };
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function submitQuery(request: QueryRequest): Promise<AnswerResponse> {
  const response = await fetch(`${API_URL}/api/v1/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`Query failed: ${response.status}`);
  }
  return response.json();
}

export function streamQuery(
  request: QueryRequest,
  onEvent: (event: RetrievalEvent) => void,
  onComplete: (answer: AnswerResponse) => void,
  onError: (error: Error) => void,
): () => void {
  const controller = new AbortController();
  fetch(`${API_URL}/api/v1/query/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
    signal: controller.signal,
  })
    .then(async (response) => {
      if (!response.ok || !response.body) {
        throw new Error(`Stream failed: ${response.status}`);
      }
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = JSON.parse(line.slice(6)) as RetrievalEvent;
            onEvent(data);
            if (data.step === "complete" && data.detail) {
              const detail = data.detail as Record<string, unknown>;
              onComplete({
                answer: detail.answer as string,
                conversation_id:
                  (detail.conversation_id as string) ||
                  request.conversation_id ||
                  "",
                citations: ((detail.citations as Partial<Citation>[]) || []).map(
                  (c) => normalizeCitation({ ...c, celex: c.celex || "" }),
                ),
                disclaimer:
                  (detail.disclaimer as string) ||
                  getDisclaimer(request.audience || "layperson"),
                retrieval_route: detail.retrieval_route as AnswerResponse["retrieval_route"],
              });
            }
          }
        }
      }
    })
    .catch(onError);
  return () => controller.abort();
}

export async function getConversation(id: string): Promise<Conversation> {
  const response = await fetch(`${API_URL}/api/v1/conversations/${id}`);
  if (!response.ok) throw new Error("Gesprek niet gevonden");
  return response.json();
}

export async function createConversation(
  queryMode: QueryMode,
  title?: string,
): Promise<{ id: string }> {
  const response = await fetch(`${API_URL}/api/v1/conversations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query_mode: queryMode, title }),
  });
  return response.json();
}

export async function getDocument(celex: string) {
  const response = await fetch(`${API_URL}/api/v1/documents/${celex}`);
  if (!response.ok) throw new Error("Document niet gevonden");
  return response.json();
}

export function getExportPdfUrl(conversationId: string): string {
  return `${API_URL}/api/v1/export/pdf/${conversationId}`;
}

export function getExportDocxUrl(conversationId: string): string {
  return `${API_URL}/api/v1/export/docx/${conversationId}`;
}

export const EXAMPLE_QUESTIONS_PRO: Record<QueryMode, string[]> = {
  open: [
    "Welke verplichtingen gelden voor high-risk AI systemen?",
    "Wat zijn de transparantie-eisen voor AI-chatbots?",
  ],
  compliance: [
    "Is mijn chatbot vergunningsplichtig onder de AI Act?",
    "Valt mijn product onder de AI Act?",
  ],
  compare: [
    "Verschil tussen GDPR artikel 6 en artikel 9?",
    "Vergelijk AI Act artikel 5 met GDPR artikel 9",
  ],
  updates: [
    "Wat is er recent gewijzigd in de AI Act?",
    "Recente wijzigingen in GDPR verordening",
  ],
};

export const EXAMPLE_QUESTIONS_LAY: Record<QueryMode, string[]> = {
  open: [
    "Mag ik klantgegevens gebruiken om mijn AI te trainen?",
    "Wat moet ik doen als mijn app persoonsgegevens verzamelt?",
  ],
  compliance: [
    "Moet ik mijn chatbot registreren bij de overheid?",
    "Geldt de AI-wet ook voor mijn kleine webshop?",
  ],
  compare: [
    "Wat is het verschil tussen toestemming en gerechtvaardigd belang?",
    "Wanneer mag ik gezondheidsdata verwerken en wanneer niet?",
  ],
  updates: [
    "Zijn er recente wijzigingen in de AI-wetgeving?",
    "Wat is er nieuw in de privacyregels voor bedrijven?",
  ],
};

/** @deprecated Use getExampleQuestions instead */
export const EXAMPLE_QUESTIONS = EXAMPLE_QUESTIONS_PRO;

export const POPULAR_QUESTIONS_LAY = [
  "Mag ik klantgegevens gebruiken om mijn AI te trainen?",
  "Moet ik mijn chatbot registreren bij de overheid?",
  "Geldt de AI-wet ook voor mijn kleine bedrijf?",
];

export const POPULAR_QUESTIONS_PRO = [
  "Welke verplichtingen gelden voor high-risk AI systemen?",
  "Is mijn chatbot vergunningsplichtig onder de AI Act?",
  "Verschil tussen GDPR artikel 6 en artikel 9?",
];

export function getExampleQuestions(
  mode: QueryMode,
  audience: "layperson" | "professional" = "layperson",
): string[] {
  const pool = audience === "layperson" ? EXAMPLE_QUESTIONS_LAY : EXAMPLE_QUESTIONS_PRO;
  return pool[mode];
}

export function getPopularQuestions(
  audience: "layperson" | "professional" = "layperson",
): string[] {
  return audience === "layperson" ? POPULAR_QUESTIONS_LAY : POPULAR_QUESTIONS_PRO;
}
