"use client";

import { CLARIFICATION_INPUT_HINT_ID } from "@/utils/clarificationView";
import { formatChoiceLabel } from "@/utils/formatChoiceLabel";
import { LaypersonMarkdown } from "./LaypersonMarkdown";
import styles from "./ClarificationPanel.module.css";

interface Props {
  intro: string;
  prompt?: string;
  options: string[];
  onSelect?: (option: string) => void;
  isDisabled?: boolean;
}

export function ClarificationPanel({
  intro,
  prompt,
  options,
  onSelect,
  isDisabled = false,
}: Props) {
  const handleSelect = (option: string) => {
    if (isDisabled) return;
    onSelect?.(option);
  };

  const choiceLegend = prompt || "Wat past het best bij uw situatie?";

  return (
    <section className={styles.panel} aria-label="Begeleiding bij uw vraag">
      <div className={styles.intro}>
        <LaypersonMarkdown>{intro}</LaypersonMarkdown>
      </div>

      {options.length > 0 && (
        <fieldset className={styles.choiceBlock} disabled={isDisabled}>
          <legend className={styles.choiceTitle}>{choiceLegend}</legend>
          <p className={styles.choiceHint}>
            Eén keuze is genoeg — daarna zoek ik de relevante EU-regels voor u op.
          </p>
          <div className={styles.chips}>
            {options.map((option) => (
              <button
                key={option}
                type="button"
                className={styles.chip}
                disabled={isDisabled}
                onClick={() => handleSelect(option)}
              >
                {formatChoiceLabel(option)}
              </button>
            ))}
          </div>
        </fieldset>
      )}

      <p id={CLARIFICATION_INPUT_HINT_ID} className={styles.footer}>
        Liever eigen woorden? Typ het antwoord in het veld hieronder.
      </p>
    </section>
  );
}
