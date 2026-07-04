"use client";

import type { Audience, LegalHypothesis } from "@/models/types";
import {
  labelLegalActor,
  labelLegalDomain,
  labelLegalEffect,
  labelEffectConclusion,
  labelPrimaryConflict,
  labelQuestionType,
  labelReconciliation,
} from "@/utils/legalHypothesisLabels";
import styles from "./LegalHypothesisPanel.module.css";

interface Props {
  hypothesis: LegalHypothesis;
  audience?: Audience;
  compact?: boolean;
  isLoading?: boolean;
}

export function LegalHypothesisPanel({
  hypothesis,
  audience = "layperson",
  compact = false,
  isLoading = false,
}: Props) {
  const title =
    audience === "layperson" ? "Juridische analyse" : "Legal case analysis (v4)";
  const evidenceLabel = isLoading
    ? "Bronnen controleren…"
    : hypothesis.evidence_valid === true
      ? "Bronnen gevalideerd"
      : hypothesis.evidence_valid === false
        ? "Onvoldoende bronnen"
        : hypothesis.reconciliation_conclusion
          ? labelReconciliation(hypothesis.reconciliation_conclusion)
          : null;

  return (
    <aside
      className={`${styles.legalHypothesisPanel} ${compact ? styles.compact : ""}`}
      aria-label={title}
    >
      <div className={styles.titleRow}>
        <h3 className={styles.title}>{title}</h3>
        {evidenceLabel && (
          <span
            className={`${styles.badge} ${
              hypothesis.evidence_valid ? styles.badgeOk : styles.badgeWarn
            }`}
          >
            {evidenceLabel}
          </span>
        )}
      </div>
      <p className={styles.problem}>{hypothesis.case_summary || hypothesis.legal_problem}</p>
      <div className={styles.metaGrid}>
        {hypothesis.primary_legal_conflict && (
          <p className={styles.metaItem}>
            <span className={styles.metaLabel}>Primair conflict</span>
            {labelPrimaryConflict(hypothesis.primary_legal_conflict)}
          </p>
        )}
        {hypothesis.legal_effect_type && (
          <p className={styles.metaItem}>
            <span className={styles.metaLabel}>Juridisch effect</span>
            {labelLegalEffect(hypothesis.legal_effect_type)}
          </p>
        )}
        {hypothesis.effect_conclusion_hint && (
          <p className={styles.metaItem}>
            <span className={styles.metaLabel}>Effectconclusie</span>
            {labelEffectConclusion(hypothesis.effect_conclusion_hint)}
          </p>
        )}
        <p className={styles.metaItem}>
          <span className={styles.metaLabel}>Rechtsgebied</span>
          {labelLegalDomain(hypothesis.legal_domain_guess)}
        </p>
        <p className={styles.metaItem}>
          <span className={styles.metaLabel}>Juridische actor</span>
          {labelLegalActor(hypothesis.legal_actor)}
        </p>
        <p className={styles.metaItem}>
          <span className={styles.metaLabel}>Vraagtype</span>
          {labelQuestionType(hypothesis.legal_question_type)}
        </p>
      </div>
      {hypothesis.likely_eu_frameworks.length > 0 && (
        <>
          <p className={styles.metaLabel}>
            {audience === "layperson" ? "Waarschijnlijk relevante EU-kaders" : "Likely EU frameworks"}
          </p>
          <ul className={styles.frameworkList}>
            {hypothesis.likely_eu_frameworks.map((framework) => (
              <li key={framework}>{framework}</li>
            ))}
          </ul>
        </>
      )}
      {audience === "layperson" && !isLoading && (
        <p className={styles.hint}>
          Dit is de juridische analyse vóór het antwoord. Het uiteindelijke antwoord volgt alleen
          als EUR-Lex-bronnen deze analyse ondersteunen.
        </p>
      )}
    </aside>
  );
}
