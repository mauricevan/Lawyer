"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Stats {
  documents_indexed: number;
  vector_points: number;
  queries_total: number;
  ingestion_jobs: Record<string, number>;
}

export default function AdminPage() {
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/api/v1/admin/stats`)
      .then((r) => r.json())
      .then(setStats)
      .catch(() => setStats(null));
  }, []);

  return (
    <main className="container">
      <header style={{ marginBottom: "2rem" }}>
        <Link href="/">← Terug</Link>
        <h1>Admin Dashboard</h1>
      </header>
      {stats ? (
        <div style={{ display: "grid", gap: "1rem", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))" }}>
          <StatCard label="Documenten" value={stats.documents_indexed} />
          <StatCard label="Vector points" value={stats.vector_points} />
          <StatCard label="Queries" value={stats.queries_total} />
          {Object.entries(stats.ingestion_jobs).map(([status, count]) => (
            <StatCard key={status} label={`Jobs: ${status}`} value={count} />
          ))}
        </div>
      ) : (
        <p>Statistieken laden...</p>
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
