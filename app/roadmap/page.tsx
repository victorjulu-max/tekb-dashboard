"use client";
import { useState } from "react";

export default function Roadmap() {
  const [hasilKota3, setHasilKota3] = useState<any>(null);
  const [hasilKota4, setHasilKota4] = useState<any>(null);
  const [loading3, setLoading3] = useState(false);
  const [loading4, setLoading4] = useState(false);

  async function jalankanKota3() {
    setLoading3(true);
    const res = await fetch('/api/kota3');
    const data = await res.json();
    setHasilKota3(data);
    setLoading3(false);
  }

  async function jalankanKota4() {
    setLoading4(true);
    const res = await fetch('/api/kota4');
    const data = await res.json();
    setHasilKota4(data);
    setLoading4(false);
  }

  return (
    <div style={{ maxWidth: "720px", margin: "0 auto", padding: "32px 20px", fontFamily: "Inter, sans-serif", color: "white", background: "#0a0a0a", minHeight: "100vh" }}>
      
      <h1 style={{ fontSize: "32px", fontWeight:900, margin:0, lineHeight:"36px" }}>🗺 PETA PERJALANAN RISET TEKB</h1>
      <p style={{ fontSize: "18px", color: "#a3a3a3", marginTop:"12px", lineHeight:"26px" }}>
        Hash: <b style={{color:"#fff"}}>575bc4d3</b> | 144 LOCKED | FROZEN v1.0<br/>
        Status saat ini: <b style={{color:"#c084fc", fontSize:"20px"}}>KOTA 4 (80%) - UJI MASA DEPAN 📍</b>
      </p>

      <div style={{display:"flex", gap:10, marginTop:20, marginBottom:28}}>
        <a href="/" style={{background:"#fff", color:"#000", padding:"12px 20px", borderRadius:12, fontSize:16, fontWeight:800, textDecoration:"none"}}>← Terminal</a>
        <a href="/api/portfolio" target="_blank" style={{background:"#1f1f1f", border:"1px solid #333", color:"#ccc", padding:"12px 20px", borderRadius:12, fontSize:16, textDecoration:"none"}}>API</a>
      </div>

      <div style={{height:12, background:"#262626", borderRadius:999, display:"flex", overflow:"hidden", marginBottom:8}}>
        <div style={{width:"20%", background:"#22c55e"}}></div>
        <div style={{width:"13%", background:"#3b82f6"}}></div>
        <div style={{width:"20%", background:"#facc15"}}></div>
        <div style={{width:"15%", background:"#c084fc"}}></div>
      </div>
      <div style={{display:"flex", justifyContent:"space-between", fontSize:13, color:"#888", marginBottom:32}}>
        <span>Kota 1 ✅</span><span>Kota 3 ✅</span><span>Kota 4 📍</span><span>Kota 5 🏁</span>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>

        <div style={{ background: "#052e16", border: "2px solid #166534", padding: "22px", borderRadius: "18px" }}>
          <div style={{ fontSize: "20px", fontWeight: 800, color: "#4ade80" }}>✅ KOTA 1: Data & Aturan Dasar</div>
          <div style={{ fontSize: "14px", background:"#166534", color:"#bbf7d0", display:"inline-block", padding:"4px 12px", borderRadius:999, marginTop:8, fontWeight:700 }}>100% SELESAI</div>
          <p style={{ fontSize: "17px", color: "#e5e5e5", marginTop: "14px", lineHeight:"28px" }}>Fondasi FROZEN v1.0 terkunci.</p>
        </div>

        <div style={{ background: "#172554", border: "2px solid #3b82f6", padding: "22px", borderRadius: "18px" }}>
          <div style={{ fontSize: "20px", fontWeight: 800, color: "#60a5fa" }}>✅ KOTA 2: 144 Kombinasi</div>
          <div style={{ fontSize: "14px", background:"#3b82f6", color:"#fff", display:"inline-block", padding:"4px 12px", borderRadius:999, marginTop:8, fontWeight:800 }}>100% SELESAI</div>
          <p style={{ fontSize: "17px", color: "#e5e5e5", marginTop: "14px", lineHeight:"28px" }}>144 kombinasi SL/TP selesai diuji.</p>
        </div>

        <div style={{ background: "#1c1c1c", border: "2px solid #22c55e", padding: "22px", borderRadius: "18px" }}>
          <div style={{ fontSize: "20px", fontWeight: 800, color: "#22c55e" }}>✅ KOTA 3: Penyaringan Ketat</div>
          <div style={{ fontSize: "14px", background:"#052e16", color:"#4ade80", display:"inline-block", padding:"4px 12px", borderRadius:999, marginTop:8, fontWeight:700 }}>SELESAI - 18 LOLOS</div>
          <div style={{marginTop:16}}>
            <button onClick={jalankanKota3} style={{background: loading3 ? '#666' : '#facc15', color:'black', padding:'14px 20px', borderRadius:12, fontSize:17, fontWeight:900, border:'none', cursor:'pointer', width:'100%'}}>
              {loading3 ? '⏳ MENYARING...' : '▶️ JALANKAN KOTA 3 LAGI'}
            </button>
            {hasilKota3 && (
              <div style={{marginTop:14, background:"#000", border:"1px solid #facc15", borderRadius:12, padding:14, fontSize:16}}>
                <div style={{color:"#facc15", fontWeight:800}}>✅ HASIL KOTA 3:</div>
                <div style={{color:"#fff", marginTop:6}}>{hasilKota3.total_kandidat} → <b style={{color:"#4ade80", fontSize:20}}>{hasilKota3.lolos_fdr} LOLOS</b></div>
              </div>
            )}
          </div>
        </div>

        <div style={{ background: "#2a1a40", border: "3px solid #c084fc", padding: "22px", borderRadius: "18px", boxShadow:"0 0 0 6px #c084fc1f" }}>
          <div style={{ fontSize: "20px", fontWeight: 800, color: "#c084fc" }}>📍 KOTA 4: Uji Masa Depan (OOS)</div>
          <div style={{ fontSize: "14px", background:"#c084fc", color:"#000", display:"inline-block", padding:"4px 12px", borderRadius:999, marginTop:8, fontWeight:800 }}>80% - KITA DI SINI SEKARANG</div>
          <p style={{ fontSize: "17px", color: "#e5e5e5", marginTop: "14px", lineHeight:"28px" }}>
            Uji 18 kandidat di data baru <b>2024-07-01 sampai hari ini</b> yang belum pernah dilihat mesin. Sekali uji, tanpa tuning.
          </p>
          <div style={{marginTop:16}}>
            <button onClick={jalankanKota4} style={{background: loading4 ? '#666' : '#c084fc', color:'black', padding:'14px 20px', borderRadius:12, fontSize:17, fontWeight:900, border:'none', cursor:'pointer', width:'100%'}}>
              {loading4 ? '⏳ SEDANG UJI MASA DEPAN...' : '🚀 JALANKAN KOTA 4 - UJI OOS'}
            </button>
            {hasilKota4 && (
              <div style={{marginTop:14, background:"#000", border:"1px solid #c084fc", borderRadius:12, padding:14, fontSize:16, lineHeight:"26px"}}>
                <div style={{color:"#c084fc", fontWeight:800}}>✅ HASIL KOTA 4:</div>
                <div style={{color:"#fff", marginTop:6}}>
                  Diuji: {hasilKota4.diuji} → <b style={{color:"#4ade80"}}>{hasilKota4.validated} VALIDATED</b> / {hasilKota4.rejected} REJECTED
                </div>
                <div style={{marginTop:10, background:"#052e16", padding:12, borderRadius:10, fontFamily:"monospace", color:"#4ade80", fontSize:16, fontWeight:700}}>
                  {hasilKota4.sinyal_final}
                </div>
                <div style={{marginTop:10, fontSize:13, color:"#aaa"}}>
                  Juara: {hasilKota4.juara_utama.id} ({hasilKota4.juara_utama.oos_return} di OOS)
                </div>
              </div>
            )}
          </div>
        </div>

        <div style={{ background: "#1c1c1c", border: "1px solid #333", padding: "22px", borderRadius: "18px" }}>
          <div style={{ fontSize: "20px", fontWeight: 800, color: "#fb7185" }}>🏁 KOTA 5: Terminal Akhir Trading</div>
          <div style={{ fontSize: "14px", background:"#3f1a22", color:"#fecdd3", display:"inline-block", padding:"4px 12px", borderRadius:999, marginTop:8, fontWeight:700 }}>TUJUAN AKHIR</div>
          <div style={{marginTop:12, background:"#000", borderRadius:12, padding:14, fontSize:18, fontFamily:"monospace", color:"#4ade80"}}>
            BUY BBCA @ 6.525<br/>SL 6.350 (-1.5 ATR) | TP 7.000 (+3 ATR)
          </div>
        </div>

      </div>
    </div>
  );
}