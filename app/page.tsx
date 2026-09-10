"use client";
import { useEffect, useState } from "react";
import Link from "next/link";

type Sinyal = {
  kode: string;
  action: "BUY" | "SELL";
  entry: number;
  sl: number;
  tp: number;
  model: string;
};

export default function Dashboard() {
  const [sinyalHariIni] = useState<Sinyal[]>([
    { kode: "BBCA", action: "BUY", entry: 6550, sl: 6350, tp: 7000, model: "Model1 RV4_BASELINE2_THRESH3" },
    { kode: "TLKM", action: "BUY", entry: 2850, sl: 2700, tp: 3150, model: "Model1 RV4_BASELINE2_THRESH3" },
  ]);
  const [loading, setLoading] = useState(false);
  const [sudahSimpan, setSudahSimpan] = useState<string[]>([]);

  const today = new Date().toISOString().slice(0, 10);

  const loadServer = async () => {
    try {
      const res = await fetch("/api/evaluasi");
      const data = await res.json();
      const hariIni = data.filter((r:any) => r.tanggal === today).map((r:any) => r.kode);
      setSudahSimpan(hariIni);
    } catch {}
  };

  useEffect(() => { loadServer(); }, []);

  const handleSimpanServer = async () => {
    setLoading(true);
    const rows = sinyalHariIni.map(s => ({
      tanggal: today,
      kode: s.kode,
      action: s.action,
      entry: s.entry,
      sl: s.sl,
      tp: s.tp,
      model: s.model,
      atr: "-1.5 / +3",
      rr: "2.0",
      vol: "144 kandidat",
      juara: "",
    }));
    const res = await fetch("/api/evaluasi", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rows }),
    });
    const json = await res.json();
    if (json.ok) {
      alert(`SUKSES SERVER! ${json.tambah} saham masuk. Total: ${json.total} data - Bisa dibuka di HP!`);
      loadServer();
    } else {
      alert("Gagal: " + json.error);
    }
    setLoading(false);
  };

  const semuaSudah = sinyalHariIni.every(s => sudahSimpan.includes(s.kode));

  return (
    <div className="min-h-screen bg-black text-white p-4 md:p-8">
      <div className="max-w-5xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl md:text-4xl font-black">TEKB TERMINAL - SERVER</h1>
          <Link href="/evaluasi" className="bg-zinc-900 border px-4 py-2 rounded-lg">📊 Evaluasi</Link>
        </div>
        <div className="grid gap-4 mb-8">
          {sinyalHariIni.map((s,i) => (
            <div key={i} className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 flex justify-between">
              <div><div className="text-3xl font-black">{s.kode} - {s.action}</div><div className="text-zinc-400">Entry {s.entry} | SL {s.sl} | TP {s.tp}</div></div>
              <div className="text-5xl">🟢</div>
            </div>
          ))}
        </div>
        <button onClick={handleSimpanServer} disabled={semuaSudah || loading} className={`w-full py-5 rounded-2xl font-black text-xl ${semuaSudah? "bg-zinc-800 text-zinc-500" : "bg-green-600 hover:bg-green-500 text-white"}`}>
          {loading? "Menyimpan ke Server..." : semuaSudah? `✅ Sudah di Server (${sudahSimpan.join(", ")})` : `💾 Simpan ${sinyalHariIni.length} Saham ke SERVER (HP & Laptop Sync)`}
        </button>
        <p className="text-center text-zinc-500 text-sm mt-4">Sekarang bisa tekan hijau dari HP! Data nyambung laptop + HP.</p>
      </div>
    </div>
  );
}