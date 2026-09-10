import { Redis } from "@upstash/redis";
import { NextResponse } from "next/server";
const redis = Redis.fromEnv();
const KEY = "evaluasi:signals";
export async function GET() {
  const real = [
    {
      tanggal:"2026-09-10", kode:"BBCA", action:"BUY", entry:6550, sl:6350, tp:7000,
      model:"Model1 RV4_BASELINE2_THRESH3", atr:"-1.5 / +3", rr:"2.0", vol:"144 kandidat", juara:"",
      signalId:"BBCA-2026-09-10-00:00-BUY", outcome:"OPEN", hitDate:null, days:0, exitPrice:null, returnPct:null, note:"Belum cukup data"
    },
    {
      tanggal:"2026-09-10", kode:"TLKM", action:"BUY", entry:2850, sl:2700, tp:3150,
      model:"Model1 RV4_BASELINE2_THRESH3", atr:"-1.5 / +3", rr:"2.0", vol:"144 kandidat", juara:"",
      signalId:"TLKM-2026-09-10-00:00-BUY", outcome:"OPEN", hitDate:null, days:0, exitPrice:null, returnPct:null, note:"Belum cukup data"
    }
  ];
  await redis.set(KEY, real);
  return NextResponse.json({ok:true, total: real.length, message:"Restore 2 real - track record bersih siap 100 entry"});
}