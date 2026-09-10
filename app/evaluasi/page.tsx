"use client";
import { useEffect, useState } from "react";
import Link from "next/link";

type Provenance = {
  provider: string;
  symbol: string;
  timeframe: string;
  evaluator_version: string;
  signal_timestamp: string;
  signal_timestamp_wib: string;
  signal_timestamp_raw: string;
  first_eval_timestamp: string | null;
  first_eval_timestamp_wib: string | null;
  last_eval_timestamp: string | null;
  last_eval_timestamp_wib: string | null;
  bars_evaluated: number;
  timeout_bars: number;
  data_start: string | null;
  data_end: string | null;
  total_bars_fetched: number;
  hit_bar?: any;
  hit_bar_index?: number;
};

export default function EvaluasiKota7() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/evaluasi/calcv2").then(r=>r.json()).then(d=>{setData(d); setLoading(false);});
  }, []);

  if (loading) return <div className="min-h-screen bg-black text-white p-8 font-mono">KOTA 7 — Loading calcv2 5m WIB provenance...</div>;
  if (!data) return <div className="min-h-screen bg-black text-white p-8">No data</div>;

  const s = data.summary;

  return (
    <div className="min-h-screen bg-black text-white p-4 md:p-8 font-mono">
      <div className="max-w- mx-auto">
        {/* HEADER */}
        <div className="flex flex-col md:flex-row justify-between gap-4 mb-6">
          <div>
            <div className="border border-zinc-700 bg-zinc-900/50 rounded-2xl p-4">
              <h1 className="text-xl md:text-2xl font-black tracking-tight">KOTA 6 — 5m EVALUATION</h1>
              <div className="text-xs text-zinc-400 mt-1">Engine: <span className="text-white font-bold">calcv2 • 5m • 78 bars • WIB</span> • {s.evaluator_version}</div>
              <div className="text- text-zinc-500 mt-1">{s.formula}</div>
            </div>
            <div className="flex flex-wrap gap-2 mt-3">
              <span className="px-3 py-1 rounded-full bg-green-900/30 border border-green-700 text-green-300 text-xs font-bold">🟢 ENGINE VALIDATED</span>
              <span className="px-3 py-1 rounded-full bg-yellow-900/30 border border-yellow-700 text-yellow-300 text-xs font-bold">🟡 HISTORICAL DATA: NOT AVAILABLE</span>
              <span className="px-3 py-1 rounded-full bg-zinc-900 border border-zinc-700 text-zinc-300 text-xs">Yahoo 5m = max 7 hari</span>
            </div>
          </div>
          <div className="flex gap-2 h-fit">
            <Link href="/api/evaluasi/calcv2" target="_blank" className="bg-zinc-900 border border-zinc-700 px-3 py-2 rounded-lg text-xs">/api/calcv2 JSON</Link>
            <Link href="/api/evaluasi/calc" target="_blank" className="bg-zinc-900 border border-zinc-700 px-3 py-2 rounded-lg text-xs">/api/calc LEGACY</Link>
            <Link href="/" className="bg-white text-black px-4 py-2 rounded-lg text-xs font-bold">← Dashboard</Link>
          </div>
        </div>

        {/* DISCLAIMER */}
        <div className="bg-yellow-950/30 border border-yellow-800/50 rounded-xl p-3 mb-6 text- text-yellow-200/80">
          <span className="font-black">LOCK:</span> ENGINE VALIDATED — NOT HISTORICAL TRACK RECORD. Badge VALIDATED di sini = logic 5m first-hit, WIB, 78 bars, provenance jalan. Bukan klaim performa historis 100 signal. Historis butuh provider 5m &gt;1 tahun.
        </div>

        {/* SUMMARY */}
        <div className="grid grid-cols-2 md:grid-cols-8 gap-3 mb-6">
          <div className="bg-zinc-900 border border-zinc-800 p-4 rounded-xl"><div className="text-zinc-500 text-">SIGNALS</div><div className="text-2xl font-black">{s.total}</div><div className="text- text-zinc-500">{s.timeframe} • {s.timeout_bars} bars</div></div>
          <div className="bg-zinc-900 border border-zinc-800 p-4 rounded-xl"><div className="text-zinc-500 text-">CLOSED</div><div className="text-2xl font-black">{s.closed}</div><div className="text- text-zinc-500">TP+SL+TO</div></div>
          <div className="bg-zinc-900 border border-zinc-800 p-4 rounded-xl"><div className="text-zinc-500 text-">OPEN</div><div className="text-2xl font-black">{s.open}</div><div className="text- text-zinc-500">{s.open>0?`${s.open} masih <78`:`done`}</div></div>
          <div className="bg-green-950/20 border border-green-900 p-4 rounded-xl"><div className="text-green-500 text-">TP_HIT</div><div className="text-2xl font-black text-green-400">{s.tp}</div></div>
          <div className="bg-red-950/20 border border-red-900 p-4 rounded-xl"><div className="text-red-500 text-">SL_HIT</div><div className="text-2xl font-black text-red-400">{s.sl}</div></div>
          <div className="bg-zinc-900 border border-zinc-800 p-4 rounded-xl"><div className="text-zinc-500 text-">TIMEOUT</div><div className="text-2xl font-black">{s.timeout}</div><div className="text- text-zinc-500">close bar 78</div></div>
          <div className="bg-yellow-950/20 border border-yellow-900 p-4 rounded-xl"><div className="text-yellow-500 text-">AMBIGUOUS</div><div className="text-2xl font-black text-yellow-400">{s.ambiguous}</div><div className="text- text-zinc-500">excluded</div></div>
          <div className="bg-zinc-900 border border-zinc-700 p-4 rounded-xl"><div className="text-zinc-500 text-">PROVIDER</div><div className="text-sm font-bold">{data.results[0]?.provenance?.provider || "yahoo"}</div><div className="text- text-zinc-500">{data.results[0]?.provenance?.total_bars_fetched} bars fetched</div></div>
        </div>

        <div className="grid md:grid-cols-2 gap-3 mb-6">
          <div className="bg-gradient-to-r from-zinc-900 to-zinc-900 border border-zinc-800 p-5 rounded-2xl">
            <div className="text- text-zinc-500">WIN RATE (CLOSED ONLY)</div>
            <div className="text-4xl font-black mt-1">{s.winRate}%</div>
            <div className="text- text-zinc-500 mt-2">TP / CLOSED — OPEN & AMBIGUOUS excluded — engine: {s.evaluator_version}</div>
          </div>
          <div className={`bg-gradient-to-r border p-5 rounded-2xl ${s.avgReturn>=0?"from-blue-950/30 to-zinc-900 border-blue-900/50":"from-red-950/30 to-zinc-900 border-red-900/50"}`}>
            <div className="text- text-zinc-500">AVG RETURN (CLOSED)</div>
            <div className={`text-4xl font-black mt-1 ${s.avgReturn>=0?"text-blue-400":"text-red-400"}`}>{s.avgReturn>0?"+":""}{s.avgReturn}%</div>
            <div className="text- text-zinc-500 mt-2">{s.engine_type}</div>
          </div>
        </div>

        {/* TRACK RECORD */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden">
          <div className="p-4 border-b border-zinc-800 flex justify-between">
            <div className="font-bold text-sm">TRACK RECORD — 5m WIB • First-Hit • 78 bars</div>
            <div className="text- text-zinc-500">Click row untuk Provenance</div>
          </div>
          <div className="overflow-auto">
            <table className="w-full text-">
              <thead className="bg-zinc-800/50 text-zinc-400">
                <tr>
                  <th className="p-3 text-left">Signal ID</th>
                  <th className="p-3 text-left">Date</th>
                  <th>Time WIB</th>
                  <th>Code</th>
                  <th>Action</th>
                  <th>Entry</th>
                  <th>SL</th>
                  <th>TP</th>
                  <th>Outcome</th>
                  <th>Hit Time WIB</th>
                  <th>Bars</th>
                  <th>Exit</th>
                  <th>Return</th>
                </tr>
              </thead>
              <tbody>
                {data.results.map((r:any)=>{
                  const isOpen = expanded===r.signalId;
                  return (
                    <>
                    <tr key={r.signalId} onClick={()=>setExpanded(isOpen?null:r.signalId)} className="border-t border-zinc-800 hover:bg-zinc-800/50 cursor-pointer">
                      <td className="p-3 font-bold text- max-w- truncate">{r.signalId}</td>
                      <td className="p-3">{r.tanggal}</td>
                      <td className="p-3 text-center">{r.jam || "00:00"}</td>
                      <td className="p-3 font-black">{r.kode}</td>
                      <td className="p-3"><span className={`px-2 py-0.5 rounded text- ${r.action==="BUY"?"bg-blue-900 text-blue-200":"bg-orange-900 text-orange-200"}`}>{r.action}</span></td>
                      <td className="p-3">{r.entry}</td>
                      <td className="p-3 text-red-300">{r.sl}</td>
                      <td className="p-3 text-green-300">{r.tp}</td>
                      <td className="p-3"><span className={`px-2 py-1 rounded font-bold text- ${r.outcome==="TP_HIT"?"bg-green-900 text-green-300": r.outcome==="SL_HIT"?"bg-red-900 text-red-300": r.outcome==="TIMEOUT"?"bg-zinc-700 text-zinc-200": r.outcome==="AMBIGUOUS_INTRABAR"?"bg-yellow-900 text-yellow-300":"bg-zinc-800 text-zinc-400"}`}>{r.outcome}</span></td>
                      <td className="p-3">{r.hitTime? `${r.hitDate} ${r.hitTime} WIB` : "-"}</td>
                      <td className="p-3">{r.bars}</td>
                      <td className="p-3">{r.exitPrice?? "-"}</td>
                      <td className={`p-3 font-bold ${r.returnPct>0?"text-green-400":r.returnPct<0?"text-red-400":""}`}>{r.returnPct!=null?(r.returnPct*100).toFixed(2)+"%":"-"}</td>
                    </tr>
                    {isOpen && (
                      <tr className="bg-zinc-950 border-t border-zinc-800">
                        <td colSpan={13} className="p-4">
                          <div className="grid md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <div className="text- font-black text-zinc-300">PROVENANCE</div>
                              <div className="bg-black border border-zinc-800 rounded-xl p-3 text- space-y-1">
                                <div className="flex justify-between"><span className="text-zinc-500">Signal Timestamp</span><span>{r.provenance.signal_timestamp_wib} ({r.provenance.signal_timestamp})</span></div>
                                <div className="flex justify-between"><span className="text-zinc-500">First Eval</span><span>{r.provenance.first_eval_timestamp_wib || "-"} </span></div>
                                <div className="flex justify-between"><span className="text-zinc-500">Last Eval</span><span>{r.provenance.last_eval_timestamp_wib || "-"} </span></div>
                                <div className="flex justify-between"><span className="text-zinc-500">Provider</span><span>{r.provenance.provider} • {r.provenance.symbol} • {r.provenance.timeframe}</span></div>
                                <div className="flex justify-between"><span className="text-zinc-500">Bars Evaluated</span><span>{r.provenance.bars_evaluated} / {r.provenance.timeout_bars}</span></div>
                                <div className="flex justify-between"><span className="text-zinc-500">Data Window</span><span className="text-">{r.provenance.data_start} → {r.provenance.data_end}</span></div>
                                <div className="flex justify-between"><span className="text-zinc-500">Total Fetched</span><span>{r.provenance.total_bars_fetched}</span></div>
                                <div className="flex justify-between"><span className="text-zinc-500">Evaluator</span><span>{r.provenance.evaluator_version}</span></div>
                              </div>
                            </div>
                            <div className="space-y-2">
                              <div className="text- font-black text-zinc-300">HIT BAR + NOTE</div>
                              <div className="bg-black border border-zinc-800 rounded-xl p-3 text-">
                                <div className="text-zinc-400 mb-2">{r.note}</div>
                                {r.provenance.hit_bar? (
                                  <div className="grid grid-cols-2 gap-2 text-">
                                    <div>Index: <b>{r.provenance.hit_bar_index}</b></div>
                                    <div>Time WIB: <b>{r.provenance.hit_bar.dateWIB} {r.provenance.hit_bar.timeWIB}</b></div>
                                    <div>Open: {r.provenance.hit_bar.open}</div>
                                    <div>High: <span className="text-green-300">{r.provenance.hit_bar.high}</span></div>
                                    <div>Low: <span className="text-red-300">{r.provenance.hit_bar.low}</span></div>
                                    <div>Close: {r.provenance.hit_bar.close}</div>
                                    <div className="col-span-2 mt-2 text- text-zinc-500">Timestamp UTC: {r.provenance.hit_bar.dateTime}</div>
                                  </div>
                                ) : <div className="text-zinc-500">No hit bar — OPEN or not yet evaluated 78 bars</div>}
                              </div>
                              <div className="text- text-zinc-500">Model: {r.model || "-"} • ATR: {(r as any).atr || "-"} • RR: {(r as any).rr || "-"}</div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                    </>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>

        <div className="mt-6 text- text-zinc-600 border-t border-zinc-800 pt-4">
          KOTA 6 v2 • calcv2 LOCKED REFERENCE ENGINE • ENGINE VALIDATED — NOT HISTORICAL TRACK RECORD • 5m • 78 bars • WIB • Provenance = reproducible • Historical 100+ signals = need 5m provider &gt;1yr
        </div>
      </div>
    </div>
  );
}