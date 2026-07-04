import type { Audience, RetrievalRoute } from "@/models/types";
import styles from "./RetrievalRouteBadge.module.css";

const PRO_LABELS: Record<RetrievalRoute, string> = {
  local: "Lokale corpus",
  live_fallback: "Live EUR-Lex",
  hybrid: "Hybride",
  cache: "Cache",
  layperson_topic: "Thema",
  cn_classification: "GN-classificatie",
  agent_flow: "EUR-Lex agent",
};

const LAY_HIDDEN: RetrievalRoute[] = ["cache"];

const LAY_LABELS: Partial<Record<RetrievalRoute, string>> = {
  local: "EU-regelgeving",
  live_fallback: "Actuele EUR-Lex",
  hybrid: "Meerdere bronnen",
  agent_flow: "Actuele EUR-Lex",
};

export function getRouteLabel(route: RetrievalRoute, audience: Audience = "professional"): string {
  if (audience === "layperson") {
    return LAY_LABELS[route] || "";
  }
  return PRO_LABELS[route];
}

interface Props {
  route?: RetrievalRoute;
  audience?: Audience;
}

export function RetrievalRouteBadge({ route, audience = "professional" }: Props) {
  if (!route) return null;
  if (audience === "layperson" && LAY_HIDDEN.includes(route)) {
    return null;
  }
  const label = getRouteLabel(route, audience);
  if (!label) return null;
  return (
    <span className={`${styles.badge} ${styles[route]}`} aria-label={`Bronroute: ${label}`}>
      {label}
    </span>
  );
}
