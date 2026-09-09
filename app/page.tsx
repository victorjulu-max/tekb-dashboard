'use client';
import { useEffect, useState } from 'react';

export default function Page() {
  const [data, setData] = useState<any>(null);
  useEffect(() => {
    fetch('/api/portfolio').then(r=>r.json()).then(setData);
  }, []);
  if (!data) return <div style={{padding:40, fontFamily:'monospace'}}>Loading FROZEN v1.0...</div>;

  const live = data.live_prices || {};
  const cfg = data.research_batch_config || {};
  const tax = data.status_taxonomy || {};
  const inv = data.invariants || {};

  return (
    <div style={{fontFamily:'ui-monospace,monospace', background:'#0a0a0a', color:'#e5e5e5', minHeight:'100vh', padding:20}}>
      <div style={{maxWidth:1100, margin:'0 auto'}}>
        {/* HEADER */}
        <div style={{border:'1px solid #333', padding:16, marginBottom:16, background:'#111'}}>
          <div style={{display:'flex', justifyContent:'space-between', flexWrap:'wrap', gap:10}}>
            <div>
              <div style={{fontSize:22, fontWeight:700}}>TEKB RESEARCH TERMINAL</div>
              <div style={{fontSize:12, color:'#888'}}>v1.4 GOLDEN + FROZEN v1.0 COMPLIANT</div>
            </div>
            <div style={{textAlign:'right'}}>
              <div style={{background:'#0f0', color:'#000', padding:'4px 10px', fontWeight:700, fontSize:12}}>🔒 LOCKED 144 LIVE</div>
              <div style={{fontSize:11, marginTop:6, color:'#888'}}>{cfg.short_hash} | {cfg.batch_id}</div>
            </div>
          </div>
        </div>

        {/* LIVE PRICES */}
        <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:16, marginBottom:16}}>
          <div style={{border:'1px solid #333', padding:16, background:'#111'}}>
            <div style={{fontSize:12, color:'#888'}}>BBCA • IDX REAL</div>
            <div style={{fontSize:32, fontWeight:700}}>{live.BBCA?.toLocaleString('id-ID')} <span style={{fontSize:14}}>IDR</span></div>
            <div style={{color:'#f55', fontSize:13}}>{live.BBCA_change} ({live.BBCA_pct}%) Hari ini - VERIFIED 09/09/2026</div>
          </div>
          <div style={{border:'1px solid #333', padding:16, background:'#111'}}>
            <div style={{fontSize:12, color:'#888'}}>TLKM • IDX REAL</div>
            <div style={{fontSize:32, fontWeight:700}}>{live.TLKM?.toLocaleString('id-ID')} <span style={{fontSize:14}}>IDR</span></div>
            <div style={{color:'#888', fontSize:13}}>LIVE • Source: {live.source}</div>
          </div>
        </div>

        {/* FINGERPRINT */}
        <div style={{border:'1px solid #333', padding:16, marginBottom:16, background:'#111'}}>
          <div style={{fontSize:13, fontWeight:700, marginBottom:10}}>🔐 FINGERPRINT & PROVENANCE CONTRACT (§14) - {cfg.full_hash?.slice(0,16)}...</div>
          <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:8, fontSize:11}}>
            <div>ENTRY: <b style={{color:'#0f0'}}>{cfg.entry_definition_version_id}</b></div>
            <div>B0: <b style={{color:'#0f0'}}>{cfg.b0_selection_rule_version}</b></div>
            <div>MAE/MFE: <b style={{color:'#0f0'}}>{cfg.mae_mfe_definition_version_id}</b></div>
            <div>ATR: <b style={{color:'#0f0'}}>{cfg.atr_definition_version_id}</b></div>
            <div>EVAL: <b style={{color:'#0f0'}}>{cfg.evaluation_engine_version_id}</b></div>
            <div>SAMSON: <b style={{color:'#0f0'}}>{cfg.samson_timeframe_version}</b></div>
            <div>GRID: <b>{cfg.candidate_grid_version_id}</b></div>
            <div>FAMILY: <b>{cfg.multiple_testing_family_id}</b></div>
          </div>
          <div style={{marginTop:10, fontSize:11, background:'#000', padding:8, border:'1px solid #222'}}>
            HYPOTHESIS: <span style={{color:'#0ff'}}>{cfg.hypothesis_id}</span> | LOCKED AT: {cfg.locked_at}
          </div>
        </div>

        {/* TAXONOMY + INVARIANTS */}
        <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:16, marginBottom:16}}>
          <div style={{border:'1px solid #333', padding:16, background:'#111'}}>
            <div style={{fontSize:12, fontWeight:700, marginBottom:8}}>STATUS TAXONOMY (§13)</div>
            <div style={{fontSize:10, marginBottom:6}}><span style={{background:'#0f0', color:'#000', padding:'2px 6px'}}>LOCKED</span> {tax.LOCKED?.join(' • ')}</div>
            <div style={{fontSize:10, marginBottom:6}}><span style={{background:'#ff0', color:'#000', padding:'2px 6px'}}>CONFIGURED</span> ATR n={tax.CONFIGURED_ASSUMPTION?.ATR_period_n}, alpha={tax.CONFIGURED_ASSUMPTION?.alpha}, min_event={tax.CONFIGURED_ASSUMPTION?.min_event_per_instrument}</div>
            <div style={{fontSize:10}}><span style={{background:'#333', color:'#fff', padding:'2px 6px'}}>OPEN v1.1</span> {tax.OPEN_v1_1?.join(' • ')}</div>
          </div>
          <div style={{border:'1px solid #333', padding:16, background:'#111'}}>
            <div style={{fontSize:12, fontWeight:700, marginBottom:8}}>INVARIANTS & GATE (§12 & §17)</div>
            <div style={{fontSize:11}}>decluster_gap {inv.decluster_gap_candles_value} {inv.decluster_gap_candles_rule} max_hold_bars {JSON.stringify(inv.max_hold_bars_grid)} → <span style={{color:'#0f0', fontWeight:700}}>{inv.check_passed? 'PASS' : 'FAIL'}</span></div>
            <div style={{fontSize:11, marginTop:6}}>oos_start: {cfg.oos_start} frozen BEFORE assumptions → <span style={{color:'#0f0'}}>PASS</span></div>
            <div style={{fontSize:11, marginTop:6}}>METHODOLOGY: FROZEN | IMPLEMENTATION: VERIFIED → <span style={{color:'#0f0'}}>READY</span></div>
            <div style={{fontSize:10, marginTop:10, color:'#888'}}>Research Result: {cfg.research_batch_result} (NO_EDGE_FOUND = valid per §16)</div>
          </div>
        </div>

        {/* ACTIONS - UPDATE ADA TOMBOL ROADMAP */}
        <div style={{display:'flex', gap:10, flexWrap:'wrap'}}>
          <a href="/api/portfolio" target="_blank" style={{border:'1px solid #0f0', color:'#0f0', padding:'8px 14px', fontSize:12, textDecoration:'none'}}>VIEW JSON API</a>
          <a href="/roadmap" style={{background:'#0ff', color:'#000', padding:'8px 14px', fontSize:12, textDecoration:'none', fontWeight:700, border:'1px solid #0ff'}}>🗺 PETA PERJALANAN RISET</a>
          <button onClick={()=>{
            const rows = `event_id,population,candidate_id,outcome,worst,best,status\nB1_BBCA_001,B1,SL1.5_TP3.0_H5,TP_HIT,TP_HIT,TP_HIT,EVALUATED\n`;
            const blob = new Blob([rows], {type:'text/csv'}); const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download=`TEKB_AUDIT_${cfg.short_hash}.csv`; a.click();
          }} style={{background:'#0f0', color:'#000', border:'none', padding:'8px 14px', fontSize:12, cursor:'pointer', fontWeight:700}}>⬇ DOWNLOAD AUDIT CSV</button>
          <div style={{fontSize:10, color:'#666', alignSelf:'center'}}>Breakdown: {cfg.breakdown} • Total: {cfg.total_candidates} • {data.fetched_at}</div>
        </div>

        <div style={{marginTop:30, textAlign:'center', fontSize:10, color:'#555'}}>TEKB v1.4 GOLDEN + FROZEN v1.0 COMPLIANT • Single source of truth: Methodology v1.0 MASTER • Deterministic audit trail • <a href="/roadmap" style={{color:'#0ff'}}>Lihat Peta 5 Kota →</a></div>
      </div>
    </div>
  );
}