"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ChatComposer } from "@/components/ChatComposer";
import { ChatThread } from "@/components/ChatThread";
import { SourcesSidebar } from "@/components/SourcesSidebar";
import { RetrievalStatus } from "@/components/RetrievalStatus";
import type { Audience, ChatMessage, Citation, QueryMode, RetrievalEvent } from "@/models/types";
import {
  getConversation,
  streamQuery,
  getExportPdfUrl,
  getExportDocxUrl,
} from "@/services/queryService";
import chatStyles from "@/components/ChatLayout.module.css";
import styles from "./page.module.css";

function createId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

function toChatMessages(
  messages: { id: string; role: string; content: string; citations?: Citation[] }[],
): ChatMessage[] {
  return messages.map((m) => ({
    id: m.id,
    role: m.role as "user" | "assistant",
    content: m.content,
    citations: m.citations,
  }));
}

export default function GesprekPage() {
  const params = useParams();
  const id = params.id as string;
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [queryMode, setQueryMode] = useState<QueryMode>("open");
  const [title, setTitle] = useState("Gesprek");
  const [followUp, setFollowUp] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [events, setEvents] = useState<RetrievalEvent[]>([]);
  const [allCitations, setAllCitations] = useState<Citation[]>([]);
  const [isReady, setIsReady] = useState(false);
  const audience: Audience = "layperson";

  useEffect(() => {
    getConversation(id)
      .then((conv) => {
        setTitle(conv.title);
        setQueryMode((conv.query_mode as QueryMode) || "open");
        setMessages(toChatMessages(conv.messages));
        setAllCitations(conv.messages.flatMap((m) => m.citations || []));
        setIsReady(true);
      })
      .catch(() => setIsReady(false));
  }, [id]);

  const handleFollowUp = (text: string) => {
    if (!text.trim() || isLoading) return;
    const pendingId = createId();
    const userId = createId();

    setIsLoading(true);
    setEvents([]);
    setFollowUp("");

    setMessages((prev) => [
      ...prev,
      { id: userId, role: "user", content: text.trim() },
      { id: pendingId, role: "assistant", content: "", isPending: true },
    ]);

    streamQuery(
      {
        question: text.trim(),
        conversation_id: id,
        query_mode: queryMode,
        audience,
        language: "nl",
      },
      (event) => setEvents((prev) => [...prev, event]),
      async (answer) => {
        setIsLoading(false);
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
        const updated = await getConversation(id);
        setAllCitations(updated.messages.flatMap((m) => m.citations || []));
      },
      () => {
        setIsLoading(false);
        setMessages((prev) => prev.filter((msg) => msg.id !== pendingId));
      },
    );
  };

  if (!isReady) {
    return (
      <main className="container">
        <p>Gesprek laden...</p>
      </main>
    );
  }

  return (
    <main className={`container ${chatStyles.chatLayout}`}>
      <header className={styles.header}>
        <Link href="/" className={styles.back}>
          ← Nieuw gesprek
        </Link>
        <h1 className={styles.title}>{title}</h1>
        <div className={styles.actions}>
          <a href={getExportPdfUrl(id)} className={styles.exportBtn}>
            Export PDF
          </a>
          <a href={getExportDocxUrl(id)} className={styles.exportBtn}>
            Export Word
          </a>
          <button
            type="button"
            className={styles.shareBtn}
            onClick={() => navigator.clipboard.writeText(window.location.href)}
          >
            Deel link
          </button>
        </div>
      </header>

      <div className={styles.layout}>
        <div className={`${styles.main} ${chatStyles.chatBody}`}>
          <ChatThread messages={messages} audience={audience} />
          <RetrievalStatus events={events} isLoading={isLoading} audience={audience} />
        </div>
        <SourcesSidebar citations={allCitations} />
      </div>

      <ChatComposer
        value={followUp}
        onChange={setFollowUp}
        onSubmit={handleFollowUp}
        isLoading={isLoading}
        isFollowUp
        variant="sticky"
      />
    </main>
  );
}
