import { LanguageSelector } from "@/components/LanguageSelector";
import styles from "./QueryFilterControls.module.css";
import type { SupportedLanguage } from "@/models/types";

const DOMAINS = [
  { id: "", label: "Alle domeinen" },
  { id: "privacy", label: "Privacy" },
  { id: "ai", label: "AI" },
  { id: "finance", label: "Financieel" },
  { id: "sustainability", label: "Duurzaamheid" },
  { id: "employment", label: "Arbeidsrecht" },
  { id: "competition", label: "Mededinging" },
];

interface Props {
  domain: string;
  timeContext: "current" | "historical";
  language: SupportedLanguage;
  onDomainChange: (domain: string) => void;
  onTimeContextChange: (timeContext: "current" | "historical") => void;
  onLanguageChange: (language: SupportedLanguage) => void;
}

export function QueryFilterControls({
  domain,
  timeContext,
  language,
  onDomainChange,
  onTimeContextChange,
  onLanguageChange,
}: Props) {
  return (
    <fieldset className={styles.fieldset}>
      <legend className={styles.legend}>Zoekfilters</legend>
      <div className={styles.row}>
        <label className={styles.label} htmlFor="domain-filter">
          Domein
        </label>
        <select
          id="domain-filter"
          className={styles.select}
          value={domain}
          onChange={(event) => onDomainChange(event.target.value)}
        >
          {DOMAINS.map((item) => (
            <option key={item.id || "all"} value={item.id}>
              {item.label}
            </option>
          ))}
        </select>
      </div>
      <div className={styles.row}>
        <span className={styles.label}>Tijdcontext</span>
        <div className={styles.toggleGroup}>
          <button
            type="button"
            className={`${styles.toggle} ${timeContext === "current" ? styles.active : ""}`}
            onClick={() => onTimeContextChange("current")}
          >
            Huidig
          </button>
          <button
            type="button"
            className={`${styles.toggle} ${timeContext === "historical" ? styles.active : ""}`}
            onClick={() => onTimeContextChange("historical")}
          >
            Historisch
          </button>
        </div>
      </div>
      <LanguageSelector language={language} onChange={onLanguageChange} />
    </fieldset>
  );
}
