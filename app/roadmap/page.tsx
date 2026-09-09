'use client';
export default function Roadmap() {
  return (
    <div style={{ maxWidth: "720px", margin: "0 auto", padding: "32px 20px", fontFamily: "Inter, sans-serif", color: "white", background: "#0a0a0a", minHeight: "100vh" }}>
      
      <h1 style={{ fontSize: "32px", fontWeight:900, margin:0, lineHeight:"36px" }}>🗺 PETA PERJALANAN RISET TEKB</h1>
      <p style={{ fontSize: "18px", color: "#a3a3a3", marginTop:"12px", lineHeight:"26px" }}>
        Hash: <b style={{color:"#fff"}}>575bc4d3</b> | 144 LOCKED | FROZEN v1.0<br/>
        Status saat ini: <b style={{color:"#60a5fa", fontSize:"20px"}}>KOTA 2 (65%) - KITA DI SINI 📍</b>
      </p>

      <div style={{display:"flex", gap:10, marginTop:20, marginBottom:28}}>
        <a href="/" style={{background:"#fff", color:"#000", padding:"12px 20px", borderRadius:12, fontSize:16, fontWeight:800, textDecoration:"none"}}>← Terminal</a>
        <a href="/api/portfolio" target="_blank" style={{background:"#1f1f1f", border:"1px solid #333", color:"#ccc", padding:"12px 20px", borderRadius:12, fontSize:16, textDecoration:"none"}}>API</a>
      </div>

      <div style={{height:12, background:"#262626", borderRadius:999, display:"flex", overflow:"hidden", marginBottom:8}}>
        <div style={{width:"20%", background:"#22c55e"}}></div>
        <div style={{width:"13%", background:"#3b82f6"}}></div>
      </div>
      <div style={{display:"flex", justifyContent:"space-between", fontSize:13, color:"#888", marginBottom:32}}>
        <span>Kota 1 ✅ 100%</span><span>Kota 2 📍 65%</span><span>Kota 5 🏁</span>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>

        {/* KOTA 1 */}
        <div style={{ background: "#052e16", border: "2px solid #166534", padding: "22px", borderRadius: "18px" }}>
          <div style={{ fontSize: "20px", fontWeight: 800, color: "#4ade80" }}>✅ KOTA 1: Data & Aturan Dasar</div>
          <div style={{ fontSize: "14px", background:"#166534", color:"#bbf7d0", display:"inline-block", padding:"4px 12px", borderRadius:999, marginTop:8, fontWeight:700 }}>100% SELESAI</div>
          <p style={{ fontSize: "17px", color: "#e5e5e5", marginTop: "14px", lineHeight:"28px" }}>
            Ambil data historis IDX, tetapkan ATR <b>n=14</b>, bekukan OOS <b>2024-07-01</b>. Fingerprint 7 layer terkunci kriptografis. Ini fondasi FROZEN v1.0.
          </p>
        </div>

        {/* KOTA 2 */}
        <div style={{ background: "#172554", border: "3px solid #3b82f6", padding: "22px", borderRadius: "18px", boxShadow:"0 0 0 6px #3b82f61f" }}>
          <div style={{ fontSize: "20px", fontWeight: 800, color: "#60a5fa" }}>📍 KOTA 2: 144 Kombinasi (In-Sample)</div>
          <div style={{ fontSize: "14px", background:"#3b82f6", color:"#fff", display:"inline-block", padding:"4px 12px", borderRadius:999, marginTop:8, fontWeight:800 }}>65% - KITA DI SINI SEKARANG</div>
          <p style={{ fontSize: "17px", color: "#e5e5e5", marginTop: "14px", lineHeight:"28px" }}>
            Mesin maraton menguji <b>144 kombinasi SL/TP</b> (6x RV × 6x BASELINE × 4x THRESH). Evaluasi via Evaluation Engine WORST/BEST sedang berjalan.
          </p>
          <div style={{marginTop:14, background:"#0f1d4a", border:"1px solid #1e3a8a", borderRadius:12, padding:14, fontSize:16, lineHeight:"24px"}}>
            Setelah ini → Kota 3 (Bootstrap & FDR) buka otomatis, lalu angka SL/TP <b>BBCA 6.525</b> muncul di Terminal.
          </div>
        </div>

        {/* KOTA 3 */}
        <div style={{ background: "#1c1c1c", border: "1px solid #333", padding: "22px", borderRadius: "18px" }}>
          <div style={{ fontSize: "20px", fontWeight: 800, color: "#facc15" }}>🚧 KOTA 3: Penyaringan Ketat</div>
          <div style={{ fontSize: "14px", background:"#422006", color:"#fde68a", display:"inline-block", padding:"4px 12px", borderRadius:999, marginTop:8, fontWeight:700 }}>SEGERA DILALUI</div>
          <p style={{ fontSize: "17px", color: "#a3a3a3", marginTop: "14px", lineHeight:"28px" }}>
            Saring kandidat dari jebakan kebetulan. Hanya yang punya Edge beneran yang lolos. Pakai Paired Bootstrap & BH-FDR.
          </p>
        </div>

        {/* KOTA 4 */}
        <div style={{ background: "#1c1c1c", border: "1px solid #333", padding: "22px", borderRadius: "18px" }}>
          <div style={{ fontSize: "20px", fontWeight: 800, color: "#c084fc" }}>⏳ KOTA 4: Uji Masa Depan (OOS)</div>
          <div style={{ fontSize: "14px", background:"#2a1a40", color:"#d8b4fe", display:"inline-block", padding:"4px 12px", borderRadius:999, marginTop:8, fontWeight:700 }}>MENUJU KE SANA</div>
          <p style={{ fontSize: "17px", color: "#a3a3a3", marginTop: "14px", lineHeight:"28px" }}>
            Uji kandidat terpilih di data baru yang belum pernah dilihat mesin. Sekali uji, tanpa tuning. Hasil final: OOS_VALIDATED / REJECTED.
          </p>
        </div>

        {/* KOTA 5 */}
        <div style={{ background: "#1c1c1c", border: "1px solid #333", padding: "22px", borderRadius: "18px" }}>
          <div style={{ fontSize: "20px", fontWeight: 800, color: "#fb7185" }}>🏁 KOTA 5: Terminal Akhir Trading</div>
          <div style={{ fontSize: "14px", background:"#3f1a22", color:"#fecdd3", display:"inline-block", padding:"4px 12px", borderRadius:999, marginTop:8, fontWeight:700 }}>TUJUAN AKHIR</div>
          <p style={{ fontSize: "17px", color: "#a3a3a3", marginTop: "14px", lineHeight:"28px" }}>
            Peta berbuah hasil. Layar jadi papan sinyal harian:
          </p>
          <div style={{marginTop:12, background:"#000", borderRadius:12, padding:14, fontSize:18, fontFamily:"monospace", color:"#4ade80"}}>
            BUY BBCA @ 6.525<br/>SL 6.350 (-1.5 ATR) | TP 7.000 (+3 ATR)
          </div>
        </div>

      </div>

      <div style={{marginTop:30, textAlign:"center", fontSize:14, color:"#666", lineHeight:"20px"}}>
        TEKB v1.4 GOLDEN + FROZEN v1.0 • 575bc4d3 • Deterministic audit trail<br/>
        Teks sekarang 17-20px, lebar 720px di tengah — tidak melebar, tidak kecil
      </div>
    </div>
  );
}