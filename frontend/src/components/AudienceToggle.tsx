import type { Audience } from "@/models/types";
import styles from "./AudienceToggle.module.css";

const OPTIONS: { id: Audience; label: string }[] = [
  { id: "layperson", label: "Begrijpelijke uitleg" },
  { id: "professional", label: "Juridische modus" },
];

interface Props {
  selectedAudience: Audience;
  onAudienceChange: (audience: Audience) => void;
}

export function AudienceToggle({ selectedAudience, onAudienceChange }: Props) {
  return (
    <fieldset className={styles.fieldset}>
      <legend className={styles.legend}>Hoe wilt u het antwoord ontvangen?</legend>
      <div className={styles.options}>
        {OPTIONS.map((option) => (
          <label
            key={option.id}
            className={`${styles.option} ${
              selectedAudience === option.id ? styles.selected : ""
            }`}
          >
            <input
              type="radio"
              name="audience"
              value={option.id}
              checked={selectedAudience === option.id}
              onChange={() => onAudienceChange(option.id)}
              className={styles.radio}
            />
            {option.label}
          </label>
        ))}
      </div>
    </fieldset>
  );
}
