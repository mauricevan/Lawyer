import type { RetrievalRoute } from "@/models/types";
import styles from "./RetrievalRouteBadge.module.css";

const LABELS: Record<RetrievalRoute, string> = {
  local: "Lokale corpus",
  live_fallback: "Live EUR-Lex",
  hybrid: "Hybride",
  cache: "Cache",
};

export function getRouteLabel(route: RetrievalRoute): string {
  return LABELS[route];
}

interface Props {
  route?: RetrievalRoute;
}

export function RetrievalRouteBadge({ route }: Props) {
  if (!route) return null;
  return (
    <span className={`${styles.badge} ${styles[route]}`} aria-label={`Bronroute: ${getRouteLabel(route)}`}>
      {getRouteLabel(route)}
    </span>
  );
}
