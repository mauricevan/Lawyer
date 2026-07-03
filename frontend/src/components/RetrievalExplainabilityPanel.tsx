"use client";

import type { RetrievalExplainability } from "@/models/types";
import styles from "./RetrievalExplainabilityPanel.module.css";

interface Props {
  explainability?: RetrievalExplainability;
}

export function RetrievalExplainabilityPanel({ explainability }: Props) {
  if (!explainability) return null;

  const { router, stage_counts: stages, sources } = explainability;

  return (
    <details className={styles.panel}>
      <summary className={styles.summary}>Retrieval details</summary>
      <dl className={styles.grid}>
        <div>
          <dt>Taal</dt>
          <dd>{explainability.query_language}</dd>
        </div>
        <div>
          <dt>Reranker</dt>
          <dd>{explainability.reranker_variant}</dd>
        </div>
        <div>
          <dt>RRF</dt>
          <dd>{explainability.hybrid_rrf_enabled ? "aan" : "uit"}</dd>
        </div>
        {router.domains.length > 0 && (
          <div>
            <dt>Domein</dt>
            <dd>{router.domains.join(", ")}</dd>
          </div>
        )}
        {router.intent_id && (
          <div>
            <dt>Intent</dt>
            <dd>{router.intent_id}</dd>
          </div>
        )}
        {router.confidence != null && (
          <div>
            <dt>Confidence</dt>
            <dd>{(router.confidence * 100).toFixed(0)}%</dd>
          </div>
        )}
        {router.domain_cluster && (
          <div>
            <dt>Cluster</dt>
            <dd>{router.domain_cluster}</dd>
          </div>
        )}
        {router.celex_hint && (
          <div>
            <dt>CELEX hint</dt>
            <dd>{router.celex_hint}</dd>
          </div>
        )}
      </dl>
      <p className={styles.stages}>
        dense {stages.dense ?? 0} · hints {stages.hints ?? 0} · merged {stages.merged ?? 0} ·
        final {stages.final ?? 0} · rerank {explainability.rerank_latency_ms.toFixed(0)}ms
      </p>
      {sources.length > 0 && (
        <ul className={styles.sources} aria-label="Bron scores">
          {sources.map((source) => (
            <li key={source.chunk_id}>
              <span>{source.celex}</span>
              <span className={styles.scores}>
                {source.vector_score != null && `vec ${source.vector_score.toFixed(2)}`}
                {source.rerank_score != null && ` · rerank ${source.rerank_score.toFixed(2)}`}
              </span>
            </li>
          ))}
        </ul>
      )}
    </details>
  );
}
