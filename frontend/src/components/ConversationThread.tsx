import type { Message } from "@/models/types";
import { CitationSources } from "./CitationSources";
import styles from "./ConversationThread.module.css";

interface Props {
  messages: Message[];
}

export function ConversationThread({ messages }: Props) {
  return (
    <div className={styles.thread}>
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`${styles.message} ${msg.role === "user" ? styles.user : styles.assistant}`}
        >
          <span className={styles.role}>
            {msg.role === "user" ? "U" : "Assistent"}
          </span>
          <div className={styles.content}>
            <p className={styles.text}>{msg.content}</p>
            {msg.citations?.length > 0 && (
              <CitationSources citations={msg.citations} />
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
