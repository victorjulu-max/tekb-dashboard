"use client";
import { useEffect, useState } from "react";

export default function PortfolioPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/portfolio", { cache: "no-store" });
      const json = await res.json();
      setData(json);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
    const id = setInterval(fetchData, 60000);
    return () => clearInterval(id);
  }, []);

  if (loading && !data) return <div style={{padding:20}}>Loading TEKB v1.4 GOLDEN...</div>;

  const live = data?.live_prices || {};
  const scan = data?.scan || [];

  return (
    <div style={{ padding: 24, fontFamily: "monospace", background: "#0a0a0a", color: "#00ff88", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 28, marginBottom: 4 }}>TEKB v1.4 GOLDEN PORTFOLIO LIVE PNL</h1>
      <div style={{ opacity: 0.7, marginBottom: 20 }}>
        {data?.status} | Engine: {data?.engine} | V14_GOLDEN: {String(data?.v14_golden)} | Fetched: {data?.fetched_at}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 24 }}>
        {scan.map((s) => {
          const avg = s.code === "BBCA" ? 9125 : 3100;
          const pnl = (((live[s.code] - avg) / avg) * 100).toFixed(2);
          const isProfit = parseFloat(pnl) > 0;
          return (
            <div key={s.code} style={{ border: "1px solid #00ff88", padding: 16, borderRadius: 12, background: "#111" }}>
              <h2 style={{ fontSize: 22 }}>{s.code} {s.action === "STRONG BUY" ? "🟢" : "🟡"}</h2>
              <div>Live: <b>Rp {live[s.code]?.toLocaleString()}</b></div>
              <div>Avg: Rp {avg.toLocaleString()}</div>
              <div>RV: <b>{s.rv} / Baseline {s.baseline}</b> = Signal {s.signal}</div>
              <div style={{ marginTop: 8, fontSize: 18, color: isProfit ? "#00ff88" : "#ff4444" }}>
                P&L: {isProfit ? "+" : ""}{pnl}%
              </div>
              <div style={{ fontSize: 12, marginTop: 6, opacity: 0.6 }}>Action: {s.action}</div>
            </div>
          );
        })}
      </div>

      <button onClick={fetchData} style={{ padding: "8px 16px", background: "#00ff88", color: "#000", border: 0, borderRadius: 8, cursor: "pointer", fontWeight: "bold" }}>
        REFRESH LIVE PRICE
      </button>

      <pre style={{ marginTop: 24, background: "#111", padding: 12, borderRadius: 8, fontSize: 11, overflow: "auto" }}>
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}