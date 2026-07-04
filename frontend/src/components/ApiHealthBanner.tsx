"use client";

import { useEffect, useState } from "react";
import { checkApiHealth, getApiUrl } from "@/services/apiClient";
import styles from "./ApiHealthBanner.module.css";

export function ApiHealthBanner() {
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    let cancelled = false;
    checkApiHealth().then((ok) => {
      if (!cancelled) setIsHealthy(ok);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  if (isHealthy !== false) return null;

  return (
    <div className={styles.banner} role="alert">
      <strong>Geen verbinding met de server.</strong>{" "}
      Controleer of de backend draait en stel{" "}
      <code>NEXT_PUBLIC_API_URL</code> in (nu: {getApiUrl()}). Zie{" "}
      <code>frontend/.env.example</code>.
    </div>
  );
}
