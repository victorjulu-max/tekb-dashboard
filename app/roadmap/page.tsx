'use client';
export default function Roadmap() {
  const cities = [
    {id:1,name:"Kota 1: Data & Aturan Dasar",status:"SELESAI",emoji:"✅",desc:"Ambil data historis IDX, ATR n=14, bekukan OOS 2024-07-01. FROZEN v1.0 & hash 575bc4d3.",details:["5m RESEARCH-ELIGIBLE","ATR Wilder smoothing","oos_start frozen BEFORE assumptions","Fingerprint 7 layer LOCKED"],color:"#0f0",progress:100},
    {id:2,name:"Kota 2: 144 Kombinasi (In-Sample)",status:"KITA DI SINI",emoji:"📍",desc:"Mesin maraton uji 144 kombinasi SL/TP (6x RV x 6x BASELINE x 4x THRESH) tahan banting.",details:["Grid SL 1-2.5 ATR, TP 1.5-4 ATR, Hold [1,3,5,10]","EQUAL_PER_EVENT pooling","MAE/MFE R1/R3/R5/R10","EVAL WORST/BEST"],color:"#0ff",progress:65},
    {id:3,name:"Kota 3: Penyaringan Ketat (Bootstrap & FDR)",status:"SEGERA",emoji:"🚧",desc:"Saring kandidat dari jebakan kebetulan. Buang jelek, sisakan Edge beneran.",details:["Paired Block Bootstrap anchor B1","BH-FDR per scenario","mean(diff)>0 & q<0.05 KEDUA skenario","Tie-break: expectancy > count > hold"],color:"#ff0",progress:0},
    {id:4,name:"Kota 4: Masa Depan (OOS Test)",status:"MENUJU",emoji:"⏳",desc:"Uji kandidat di data baru belum pernah dilihat. Pastikan tidak kaget di pasar sungguhan.",details:["Sekali uji tanpa tuning","Tanpa FDR","OOS_VALIDATED / REJECTED = final","Window OOS spent/tainted"],color:"#888",progress:0},
    {id:5,name:"Kota 5: Terminal Akhir (Live Signal)",status:"TUJUAN AKHIR",emoji:"🏁",desc:"Peta berbuah hasil. Layar jadi papan sinyal: BBCA apa, entry berapa, SL/TP berapa.",details:["BBCA Entry 6525, SL=Entry-1.5*ATR, TP=Entry+3*ATR","Live Execution & Signal Board","Realized PnL R-unit","Daily briefing 09:00 WIB"],color:"#f0f",progress:0},
  ];
  return (
    <div style={{fontFamily:'monospace',background:'#080808',color:'#e5e5e5',minHeight:'100vh',padding:20}}>
      <div style={{maxWidth:1000,margin:'0 auto'}}>
        <div style={{border:'1px solid #333',padding:16,marginBottom:20,background:'#111'}}>
          <div style={{fontSize:20,fontWeight:700}}>🗺 PETA PERJALANAN RISET TEKB</div>
          <div style={{fontSize:12,color:'#888',marginTop:4}}>Research Pipeline & Milestone — FROZEN v1.0 → Live Signal • Hash 575bc4d3 • 144 LOCKED</div>
          <div style={{marginTop:12,display:'flex',gap:8}}><a href="/" style={{border:'1px solid #0f0',color:'#0f0',padding:'6px 12px',fontSize:11,textDecoration:'none'}}>← TERMINAL</a><a href="/api/portfolio" target="_blank" style={{border:'1px solid #333',color:'#888',padding:'6px 12px',fontSize:11,textDecoration:'none'}}>API JSON</a></div>
        </div>
        <div style={{border:'1px solid #333',padding:12,marginBottom:20,background:'#111'}}>
          <div style={{fontSize:11,marginBottom:8}}>PROGRESS: Kota 1 Selesai → Kota 2 (65%) → Kota 5 Tujuan</div>
          <div style={{height:10,background:'#222',display:'flex'}}><div style={{width:'20%',background:'#0f0'}}></div><div style={{width:'13%',background:'#0ff'}}></div><div style={{width:'67%',background:'#222'}}></div></div>
          <div style={{display:'flex',justifyContent:'space-between',fontSize:9,color:'#666',marginTop:4}}><span>Kota 1 ✅</span><span>Kota 2 📍 65%</span><span>Kota 3 🚧</span><span>Kota 4 ⏳</span><span>Kota 5 🏁</span></div>
        </div>
        <div style={{position:'relative'}}><div style={{position:'absolute',left:24,top:20,bottom:20,width:2,background:'#222'}}></div>
          {cities.map(c=>(
            <div key={c.id} style={{display:'flex',gap:16,marginBottom:20,position:'relative'}}>
              <div style={{width:48,height:48,borderRadius:'50%',background:'#111',border:`2px solid ${c.color}`,display:'flex',alignItems:'center',justifyContent:'center',fontSize:20,zIndex:1}}>{c.emoji}</div>
              <div style={{flex:1,border:`1px solid ${c.color}55`,background:'#111',padding:14}}>
                <div style={{display:'flex',justifyContent:'space-between',flexWrap:'wrap',gap:8}}><div style={{fontSize:13,fontWeight:700,color:c.color}}>{c.name}</div><div style={{fontSize:10,background:c.color,color:'#000',padding:'2px 8px',fontWeight:700}}>{c.status} {c.progress>0?`${c.progress}%`:''}</div></div>
                <div style={{fontSize:11,color:'#ccc',marginTop:8}}>{c.desc}</div>
                <div style={{marginTop:10,display:'grid',gridTemplateColumns:'1fr 1fr',gap:6}}>{c.details.map((d,i)=>(<div key={i} style={{fontSize:10,background:'#000',border:'1px solid #222',padding:'6px 8px',color:'#aaa'}}>• {d}</div>))}</div>
                {c.id===2 && <div style={{marginTop:10,background:'#001a1a',border:'1px solid #0ff',padding:8,fontSize:10}}>📍 POSISI SEKARANG: Grid 144 dievaluasi via Evaluation Engine. Setelah ini → Bootstrap & FDR (Kota 3) buka otomatis, lalu SL/TP muncul di Terminal Utama.</div>}
              </div>
            </div>
          ))}
        </div>
        <div style={{border:'1px solid #0f0',background:'#001100',padding:12,marginTop:10,fontSize:11}}><b style={{color:'#0f0'}}>ANALOGI:</b> Seperti peta subway. Kota 1 sudah lewat, Kota 2 lab 144 stasiun kita sekarang. Begitu 144 selesai, gerbang Kota 3-5 terbuka otomatis sampai SL/TP BBCA 6525 muncul di layar utama.</div>
        <div style={{textAlign:'center',marginTop:20,fontSize:10,color:'#555'}}>TEKB v1.4 GOLDEN + FROZEN v1.0 COMPLIANT • Hash 575bc4d3 • Deterministic audit trail</div>
      </div>
    </div>
  );
}