"use client";

import { useState } from "react";
import type { Audience, Citation } from "@/models/types";
import { CopyCitationButton } from "./CopyCitationButton";
import styles from "./TrustCard.module.css";

interface Props {
  citation: Citation;
  audience?: Audience;
}

export function TrustCard({ citation, audience = "layperson" }: Props) {
  const [showDetails, setShowDetails] = useState(false);
  const { trust } = citation;
  const isLayperson = audience === "layperson";

  const articleLabel = isLayperson
    ? citation.title || `EU-regelgeving (artikel ${citation.article || "?"})`
    : citation.article
      ? `Artikel ${citation.article}`
      : citation.title || citation.celex;

  return (
    <article className={styles.card}>
      <header className={styles.header}>
        <h3 className={styles.title}>{articleLabel}</h3>
        {!isLayperson && citation.title && citation.article && (
          <p className={styles.subtitle}>{citation.title}</p>
        )}
      </header>
      <div className={styles.badges}>
        {trust.is_consolidated && (
          <span className={styles.badgeSuccess}>
            {isLayperson ? "Officiële bijgewerkte versie" : "Geconsolideerde versie"}
          </span>
        )}
        {trust.is_in_force && (
          <span className={styles.badgeSuccess}>
            {isLayperson ? "Nog van kracht" : "In werking"}
          </span>
        )}
        {!trust.is_in_force && (
          <span className={styles.badgeWarning}>
            {isLayperson ? "Niet meer geldig" : "Niet meer in werking"}
          </span>
        )}
      </div>
      {citation.excerpt && (
        <blockquote className={styles.excerpt}>{citation.excerpt}</blockquote>
      )}
      <div className={styles.actions}>
        <a
          href={citation.eurlex_url}
          target="_blank"
          rel="noopener noreferrer"
          className={styles.link}
        >
          Bekijk op EUR-Lex
        </a>
        {isLayperson ? (
          <button
            type="button"
            className={styles.detailsToggle}
            onClick={() => setShowDetails((prev) => !prev)}
            aria-expanded={showDetails}
          >
            {showDetails ? "Minder details" : "Meer details"}
          </button>
        ) : (
          <CopyCitationButton citation={citation} />
        )}
      </div>
      {isLayperson && showDetails && (
        <div className={styles.details}>
          <div className={styles.meta}>
            {citation.celex && <span>CELEX: {citation.celex}</span>}
            {trust.last_modified && <span>Laatste update: {trust.last_modified}</span>}
            {trust.oj_reference && <span>OJ {trust.oj_reference}</span>}
          </div>
          {trust.has_corrigendum && (
            <div className={styles.warning} role="alert">
              Er bestaat een correctie op deze tekst
              {trust.corrigendum_celex && ` (${trust.corrigendum_celex})`}
            </div>
          )}
          <CopyCitationButton citation={citation} />
        </div>
      )}
      {!isLayperson && (
        <>
          {(citation.retrieval_score != null || citation.rerank_score != null) && (
            <div className={styles.meta}>
              {citation.retrieval_score != null && (
                <span>Vector: {citation.retrieval_score.toFixed(2)}</span>
              )}
              {citation.rerank_score != null && (
                <span>Rerank: {citation.rerank_score.toFixed(2)}</span>
              )}
            </div>
          )}
          <div className={styles.meta}>
            {trust.last_modified && <span>Laatste update: {trust.last_modified}</span>}
            {trust.oj_reference && <span>OJ {trust.oj_reference}</span>}
          </div>
          {trust.has_corrigendum && (
            <div className={styles.warning} role="alert">
              Er bestaat een corrigendum
              {trust.corrigendum_celex && ` (${trust.corrigendum_celex})`}
            </div>
          )}
        </>
      )}
    </article>
  );
}
