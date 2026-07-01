import type { Audience, QueryMode } from "@/models/types";
import styles from "./GuidedQuerySelector.module.css";

const LAY_MODES: { id: QueryMode; label: string; description: string }[] = [
  {
    id: "open",
    label: "Ik wil weten wat de regels zeggen",
    description: "Algemene uitleg in gewone taal",
  },
  {
    id: "compliance",
    label: "Geldt dit voor mijn situatie?",
    description: "Persoonlijke toepasbaarheid",
  },
  {
    id: "compare",
    label: "Wat is het verschil tussen...?",
    description: "Verschillen helder uitgelegd",
  },
  {
    id: "updates",
    label: "Zijn er recente wijzigingen?",
    description: "Actuele ontwikkelingen",
  },
];

const PRO_MODES: { id: QueryMode; label: string; description: string }[] = [
  { id: "open", label: "Wat zegt de wet over...", description: "Open juridische vraag" },
  { id: "compliance", label: "Geldt [verordening] voor mij?", description: "Compliance check" },
  { id: "compare", label: "Vergelijk artikel X met Y", description: "Artikelvergelijking" },
  { id: "updates", label: "Wat is er recent gewijzigd in?", description: "Update tracking" },
];

interface Props {
  selectedMode: QueryMode;
  audience: Audience;
  onModeChange: (mode: QueryMode) => void;
}

export function GuidedQuerySelector({ selectedMode, audience, onModeChange }: Props) {
  const modes = audience === "layperson" ? LAY_MODES : PRO_MODES;

  return (
    <fieldset className={styles.fieldset}>
      <legend className={styles.legend}>Wat wilt u weten?</legend>
      <div className={styles.grid}>
        {modes.map((mode) => (
          <label
            key={mode.id}
            className={`${styles.option} ${selectedMode === mode.id ? styles.selected : ""}`}
          >
            <input
              type="radio"
              name="query-mode"
              value={mode.id}
              checked={selectedMode === mode.id}
              onChange={() => onModeChange(mode.id)}
              className={styles.radio}
            />
            <span className={styles.label}>{mode.label}</span>
            <span className={styles.description}>{mode.description}</span>
          </label>
        ))}
      </div>
    </fieldset>
  );
}
