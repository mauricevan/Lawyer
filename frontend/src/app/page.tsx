"use client";

import { useState } from "react";
import { AudienceToggle } from "@/components/AudienceToggle";
import { ChatComposer } from "@/components/ChatComposer";
import { ChatThread } from "@/components/ChatThread";
import { GuidedQuerySelector } from "@/components/GuidedQuerySelector";
import { ExampleQuestions } from "@/components/ExampleQuestions";
import { RetrievalStatus } from "@/components/RetrievalStatus";
import type { Audience, ChatMessage, QueryMode, RetrievalEvent } from "@/models/types";
import {
  getDisclaimer,
  getExampleQuestions,
  getPopularQuestions,
  streamQuery,
} from "@/services/queryService";
import chatStyles from "@/components/ChatLayout.module.css";
import styles from "./page.module.css";

const COPY = {
  layperson: {
    title: "Uw vraag over EU-regels, helder uitgelegd",
    subtitle: "Beschrijf uw situatie en ontvang een begrijpelijk antwoord op basis van EUR-Lex",
  },
  professional: {
    title: "EU Juridisch Onderzoek",
    subtitle: "Stel vragen over EU-wetgeving met bronverwijzingen naar EUR-Lex",
  },
} as const;

const MODE_LABELS: Record<QueryMode, string> = {
  open: "Algemene vraag",
  compliance: "Geldt voor mij?",
  compare: "Vergelijking",
  updates: "Recente wijzigingen",
};

function createId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export default function HomePage() {
  const [queryMode, setQueryMode] = useState<QueryMode>("open");
  const [audience, setAudience] = useState<Audience>("layperson");
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [events, setEvents] = useState<RetrievalEvent[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [lockedAudience, setLockedAudience] = useState<Audience | null>(null);
  const [lockedMode, setLockedMode] = useState<QueryMode | null>(null);

  const isChatActive = messages.length > 0;
  const activeAudience = lockedAudience ?? audience;
  const copy = COPY[activeAudience];

  const resetConversation = () => {
    setMessages([]);
    setConversationId(undefined);
    setEvents([]);
    setError(null);
    setQuestion("");
    setLockedAudience(null);
    setLockedMode(null);
  };

  const runQuery = (queryText: string) => {
    if (!queryText.trim() || isLoading) return;

    const userId = createId();
    const pendingId = createId();

    if (!lockedAudience) setLockedAudience(audience);
    if (!lockedMode) setLockedMode(queryMode);

    setIsLoading(true);
    setError(null);
    setEvents([]);
    setQuestion("");

    setMessages((prev) => [
      ...prev,
      { id: userId, role: "user", content: queryText.trim() },
      { id: pendingId, role: "assistant", content: "", isPending: true },
    ]);

    streamQuery(
      {
        question: queryText.trim(),
        query_mode: lockedMode ?? queryMode,
        audience: lockedAudience ?? audience,
        language: "nl",
        conversation_id: conversationId,
      },
      (event) => setEvents((prev) => [...prev, event]),
      (answer) => {
        setIsLoading(false);
        if (answer.conversation_id) {
          setConversationId(answer.conversation_id);
        }
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === pendingId
              ? {
                  id: pendingId,
                  role: "assistant",
                  content: answer.answer,
                  citations: answer.citations,
                }
              : msg,
          ),
        );
      },
      (err) => {
        setIsLoading(false);
        setError(err.message);
        setMessages((prev) => prev.filter((msg) => msg.id !== pendingId));
      },
    );
  };

  if (isChatActive) {
    return (
      <main className={`container ${chatStyles.chatLayout}`}>
        <header className={styles.chatHeader}>
          <div>
            <h1 className={styles.chatTitle}>{copy.title}</h1>
            <div className={styles.badges}>
              <span className={styles.badge}>
                {activeAudience === "layperson" ? "Begrijpelijke uitleg" : "Juridische modus"}
              </span>
              {lockedMode && <span className={styles.badge}>{MODE_LABELS[lockedMode]}</span>}
            </div>
          </div>
          <button type="button" className={styles.newChatBtn} onClick={resetConversation}>
            Nieuw gesprek
          </button>
        </header>

        <div className={chatStyles.chatBody}>
          <ChatThread messages={messages} audience={activeAudience} />
          <RetrievalStatus events={events} isLoading={isLoading} audience={activeAudience} />
          {error && (
            <p className={styles.error} role="alert">
              {error}
            </p>
          )}
        </div>

        <ChatComposer
          value={question}
          onChange={setQuestion}
          onSubmit={runQuery}
          isLoading={isLoading}
          isFollowUp
          variant="sticky"
        />

        <p className={styles.disclaimerCompact}>{getDisclaimer(activeAudience)}</p>
      </main>
    );
  }

  return (
    <main className="container">
      <header className={styles.header}>
        <h1 className={styles.title}>{copy.title}</h1>
        <p className={styles.subtitle}>{copy.subtitle}</p>
      </header>

      <div className={styles.onboarding}>
        <AudienceToggle selectedAudience={audience} onAudienceChange={setAudience} />

        <GuidedQuerySelector
          selectedMode={queryMode}
          audience={audience}
          onModeChange={setQueryMode}
        />

        <div className={styles.questionSection}>
          <ChatComposer
            value={question}
            onChange={setQuestion}
            onSubmit={runQuery}
            isLoading={isLoading}
            label="Uw vraag"
            variant="landing"
          />
          <RetrievalStatus events={events} isLoading={isLoading} audience={audience} />
          {error && (
            <p className={styles.error} role="alert">
              {error}
            </p>
          )}
        </div>

        <div className={styles.examplesSection}>
          <ExampleQuestions
            questions={getExampleQuestions(queryMode, audience)}
            onSelect={setQuestion}
          />
          <ExampleQuestions
            questions={getPopularQuestions(audience)}
            onSelect={setQuestion}
            title="Populaire vragen"
          />
        </div>
      </div>

      <p className={styles.disclaimer}>{getDisclaimer(audience)}</p>
    </main>
  );
}
