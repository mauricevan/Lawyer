import styles from "./LanguageSelector.module.css";
import type { SupportedLanguage } from "@/models/types";

const OPTIONS: { id: SupportedLanguage; label: string }[] = [
  { id: "auto", label: "Automatisch" },
  { id: "nl", label: "Nederlands" },
  { id: "en", label: "English" },
  { id: "fr", label: "Français" },
  { id: "de", label: "Deutsch" },
  { id: "es", label: "Español" },
];

interface Props {
  language: SupportedLanguage;
  onChange: (language: SupportedLanguage) => void;
}

export function LanguageSelector({ language, onChange }: Props) {
  return (
    <div className={styles.row}>
      <label className={styles.label} htmlFor="language-select">
        Taal
      </label>
      <select
        id="language-select"
        className={styles.select}
        value={language}
        onChange={(event) => onChange(event.target.value as SupportedLanguage)}
      >
        {OPTIONS.map((option) => (
          <option key={option.id} value={option.id}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}
