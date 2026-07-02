"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { fetchAdmin, getStoredAdminKey, storeAdminKey } from "@/services/adminApi";

interface Stats {
  documents_indexed: number;
  vector_points: number;
  queries_total: number;
  live_cache_entries?: number;
  live_cache_hits_total?: number;
  audit_events_total?: number;
  runtime_metrics?: Record<string, unknown>;
  feature_flags?: Record<string, boolean>;
  ingestion_jobs: Record<string, number>;
}

interface CacheStatus {
  redis: { status: string };
  live_cache: {
    total_entries: number;
    active_entries: number;
    expired_entries: number;
    top_celex: Array<{ celex: string; hits: number }>;
  };
}

export default function AdminPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [cache, setCache] = useState<CacheStatus | null>(null);
  const [adminKey, setAdminKey] = useState("");
  const [error, setError] = useState<string | null>(null);

  const loadDashboard = useCallback(async () => {
    setError(null);
    try {
      const [statsResponse, cacheResponse] = await Promise.all([
        fetchAdmin("/stats"),
        fetchAdmin("/cache"),
      ]);
      if (!statsResponse.ok) {
        setError(statsResponse.status === 403 ? "Admin key ontbreekt of is ongeldig." : "Kon stats niet laden.");
        setStats(null);
        setCache(null);
        return;
      }
      setStats(await statsResponse.json());
      setCache(cacheResponse.ok ? await cacheResponse.json() : null);
    } catch {
      setError("Kon geen verbinding maken met de API.");
      setStats(null);
      setCache(null);
    }
  }, []);

  useEffect(() => {
    setAdminKey(getStoredAdminKey());
    loadDashboard();
  }, [loadDashboard]);

  function handleSaveKey() {
    storeAdminKey(adminKey);
    loadDashboard();
  }

  return (
    <main className="container">
      <header style={{ marginBottom: "2rem" }}>
        <Link href="/">← Terug</Link>
        <h1>Admin Dashboard</h1>
      </header>
      <section style={{ marginBottom: "1.5rem", display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
        <label style={{ flex: "1 1 280px" }}>
          <span style={{ display: "block", marginBottom: "0.25rem" }}>Admin API key</span>
          <input
            type="password"
            value={adminKey}
            onChange={(event) => setAdminKey(event.target.value)}
            placeholder="X-Admin-Key"
            style={{ width: "100%", minHeight: "44px", padding: "0.5rem 0.75rem" }}
          />
        </label>
        <button type="button" onClick={handleSaveKey} style={{ alignSelf: "flex-end", minHeight: "44px" }}>
          Opslaan & verversen
        </button>
      </section>
      {error && <p role="alert" style={{ color: "#dc2626" }}>{error}</p>}
      {stats ? (
        <>
          <div style={{ display: "grid", gap: "1rem", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))" }}>
            <StatCard label="Documenten" value={stats.documents_indexed} />
            <StatCard label="Vector points" value={stats.vector_points} />
            <StatCard label="Queries" value={stats.queries_total} />
            <StatCard label="Live cache entries" value={stats.live_cache_entries ?? 0} />
            <StatCard label="Cache hits" value={stats.live_cache_hits_total ?? 0} />
            <StatCard label="Audit events" value={stats.audit_events_total ?? 0} />
            {Object.entries(stats.ingestion_jobs).map(([status, count]) => (
              <StatCard key={status} label={`Jobs: ${status}`} value={count} />
            ))}
          </div>
          {stats.feature_flags && (
            <section style={{ marginTop: "2rem" }}>
              <h2>Feature flags</h2>
              <ul>
                {Object.entries(stats.feature_flags).map(([key, enabled]) => (
                  <li key={key}>{key}: {enabled ? "aan" : "uit"}</li>
                ))}
              </ul>
            </section>
          )}
          {stats.runtime_metrics && (
            <section style={{ marginTop: "2rem" }}>
              <h2>Runtime metrics</h2>
              <pre style={{ background: "#f8fafc", padding: "1rem", borderRadius: "8px", overflow: "auto" }}>
                {JSON.stringify(stats.runtime_metrics, null, 2)}
              </pre>
            </section>
          )}
        </>
      ) : !error ? (
        <p>Statistieken laden...</p>
      ) : null}
      {cache && (
        <section style={{ marginTop: "2rem" }}>
          <h2>Cache status</h2>
          <p>Redis: {cache.redis.status}</p>
          <p>Live cache actief: {cache.live_cache.active_entries} / {cache.live_cache.total_entries}</p>
          <p>Verlopen: {cache.live_cache.expired_entries}</p>
        </section>
      )}
    </main>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div style={{
      padding: "1.5rem",
      background: "white",
      border: "1px solid #e2e8f0",
      borderRadius: "8px",
    }}>
      <p style={{ margin: 0, color: "#4a5568", fontSize: "0.875rem" }}>{label}</p>
      <p style={{ margin: "0.5rem 0 0", fontSize: "2rem", fontWeight: 600 }}>{value}</p>
    </div>
  );
}
