"use client";
import { useEffect, useState } from "react";
import Link from "next/link";

export default function Evaluasi() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/evaluasi/calc").then(r=>r.json()).then(d=>{setData(d); setLoading(false);});
  }, []);

  if (loading) return <div className="min-h-screen bg-black text-white p-8">Hitung evaluasi MASTER... fetch Yahoo Finance...</div>;

  const s = data.summary;
  return (
    <div className="min-h-screen bg-black text-white p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between mb-6">
          <h1 className="text-2xl font-black">📊 EVALUASI MASTER - {s.total} Sinyal</h1>
          <Link href="/" className="bg-zinc-900 border px-4 py-2 rounded-lg">← Dashboard</Link>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-6 gap-3 mb-6">
          <div className="bg-zinc-900 p-4 rounded-xl"><div className="text-zinc-400 text-xs">CLOSED (denominator)</div><div className="text-2xl font-bold">{s.closed}</div><div className="text-xs text-zinc-500">TP+SL+TIMEOUT</div></div>
          <div className="bg-green-900/30 border border-green-800 p-4 rounded-xl"><div className="text-green-400 text-xs">TP_HIT</div><div className="text-2xl font-bold text-green-400">{s.tp}</div></div>
          <div className="bg-red-900/30 border border-red-800 p-4 rounded-xl"><div className="text-red-400 text-xs">SL_HIT</div><div className="text-2xl font-bold text-red-400">{s.sl}</div></div>
          <div className="bg-zinc-800 p-4 rounded-xl"><div className="text-zinc-400 text-xs">TIMEOUT</div><div className="text-2xl font-bold">{s.timeout}</div></div>
          <div className="bg-yellow-900/30 border border-yellow-800 p-4 rounded-xl"><div className="text-yellow-400 text-xs">AMBIGUOUS</div><div className="text-2xl font-bold text-yellow-400">{s.ambiguous}</div><div className="text- text-zinc-500">SL & TP same day</div></div>
          <div className="bg-zinc-800 p-4 rounded-xl"><div className="text-zinc-400 text-xs">OPEN</div><div className="text-2xl font-bold">{s.open}</div></div>
        </div>

        <div className="bg-gradient-to-r from-green-900/50 to-zinc-900 border border-green-800 p-6 rounded-2xl mb-6">
          <div className="text-sm text-zinc-400">WIN RATE (MASTER FORMULA)</div>
          <div className="text-5xl font-black text-green-400">{s.winRate}%</div>
          <div className="text-xs text-zinc-500 mt-2">{s.formula}</div>
          <div className="text-xs text-yellow-500 mt-1">⚠️ AMBIGUOUS & OPEN tidak masuk hitungan — tidak menyesatkan</div>
        </div>

        <div className="bg-zinc-900 rounded-xl overflow-auto">
          <table className="w-full text-sm">
            <thead className="bg-zinc-800"><tr><th className="p-3 text-left">Tgl</th><th>Kode</th><th>Outcome</th><th>Hit Date</th><th>Days</th><th>Catatan</th></tr></thead>
            <tbody>
              {data.results.map((r:any,i:number)=>
                <tr key={i} className="border-t border-zinc-800">
                  <td className="p-3">{r.tanggal}</td><td className="font-bold">{r.kode}</td>
                  <td><span className={`px-2 py-1 rounded text-xs font-bold ${r.outcome==="TP_HIT"?"bg-green-900 text-green-300": r.outcome==="SL_HIT"?"bg-red-900 text-red-300": r.outcome==="AMBIGUOUS_INTRABAR"?"bg-yellow-900 text-yellow-300": "bg-zinc-800 text-zinc-300"}`}>{r.outcome}</span></td>
                  <td>{r.hitDate || "-"}</td><td>{r.days}</td><td className="text-zinc-400 text-xs">{r.note}</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}