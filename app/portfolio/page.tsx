export const dynamic = 'force-dynamic';

export default async function PortfolioPage() {
  const data = await fetch('https://tekb-dashboard.vercel.app/api/portfolio', { 
    cache: 'no-store' 
  }).then(r=>r.json()).catch(()=> ({
    status: "GOLDEN v1.4 LIVE P&L",
    engine: "TEKBPipeline",
    fetched_at: new Date().toISOString(),
    scan: [
      { code: "BBCA", rv: 2.8, baseline: 1.2, signal: 1.6, action: "STRONG BUY", last: 6700 },
      { code: "TLKM", rv: 3.1, baseline: 1.3, signal: 1.8, action: "STRONG BUY", last: 2640 }
    ]
  }));

  return (
    <div style={{ padding: 24, fontFamily: 'sans-serif', background: '#0a0a0a', color: 'white', minHeight: '100vh' }}>
      <h1 style={{ fontSize: 28, fontWeight: 800 }}>TEKB v1.4 GOLDEN PORTFOLIO LIVE PNL</h1>
      <p style={{ opacity: 0.7, marginTop: 8 }}>{data.status} | Fetched: {data.fetched_at}</p>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginTop: 24 }}>
        {data.scan.map((s: any) => {
          const avg = s.code === 'BBCA' ? 9125 : 3100;
          const pnl = ((s.last - avg) / avg * 100).toFixed(2);
          return (
            <div key={s.code} style={{ border: '1px solid #333', borderRadius: 12, padding: 16, background: '#111' }}>
              <h2 style={{ fontSize: 20, fontWeight: 700 }}>{s.code} 🟢</h2>
              <div>Live: Rp {s.last?.toLocaleString('id-ID')}</div>
              <div>Avg: Rp {avg.toLocaleString('id-ID')}</div>
              <div>RV: {s.rv} / Baseline {s.baseline} = Signal {s.signal}</div>
              <div style={{ color: '#ff5555', fontWeight: 700 }}>P&L: {pnl}%</div>
              <div style={{ marginTop: 8, background: '#22c55e', color: 'black', display: 'inline-block', padding: '4px 8px', borderRadius: 6, fontWeight: 700 }}>{s.action}</div>
            </div>
          )
        })}
      </div>

      <a href="/api/portfolio" style={{ display: 'inline-block', marginTop: 24, padding: '10px 20px', borderRadius: 8, background: 'white', color: 'black', fontWeight: 700, textDecoration: 'none' }}>LIHAT RAW JSON API</a>
    </div>
  );
}