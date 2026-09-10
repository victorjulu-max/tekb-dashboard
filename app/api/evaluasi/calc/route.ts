import { Redis } from "@upstash/redis";
import { NextResponse } from "next/server";

export const runtime = "edge";
const redis = Redis.fromEnv();

const TIMEOUT_DAYS = 20;

type Signal = { tanggal: string; kode: string; entry: number; sl: number; tp: number; action: "BUY"|"SELL" };

async function fetchOHLC(kode: string, fromDate: string) {
  const symbol = `${kode}.JK`;
  const period1 = Math.floor(new Date(fromDate).getTime()/1000);
  const period2 = period1 + 60*24*3600;
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?period1=${period1}&period2=${period2}&interval=1d&includeAdjustedClose=true`;
  try {
    const res = await fetch(url, { headers: { "User-Agent": "Mozilla/5.0" } });
    const json = await res.json();
    const result = json.chart?.result?.[0];
    if (!result) return [];
    const timestamps = result.timestamp || [];
    const quote = result.indicators?.quote?.[0];
    const highs = quote?.high || [];
    const lows = quote?.low || [];
    const closes = quote?.close || [];
    return timestamps.map((t:number,i:number)=> ({
      date: new Date(t*1000).toISOString().slice(0,10),
      high: highs[i],
      low: lows[i],
      close: closes[i],
    })).filter((d:any)=> d.high!= null);
  } catch { return []; }
}

function evaluateSignal(sig: Signal, ohlc: any[]) {
  const startIdx = ohlc.findIndex((d:any)=> d.date > sig.tanggal);
  const slice = startIdx >=0? ohlc.slice(startIdx, startIdx+TIMEOUT_DAYS) : [];

  for (let i=0; i<slice.length; i++) {
    const d = slice[i];
    const hitTP = d.high >= sig.tp;
    const hitSL = d.low <= sig.sl;

    if (hitTP && hitSL) {
      return { outcome: "AMBIGUOUS_INTRABAR" as const, hitDate: d.date, days: i+1, exitPrice: null, returnPct: null, note: `High ${d.high} >= TP ${sig.tp} & Low ${d.low} <= SL ${sig.sl}` };
    }
    if (hitTP) {
      const exitPrice = sig.tp;
      const returnPct = (exitPrice - sig.entry) / sig.entry;
      return { outcome: "TP_HIT" as const, hitDate: d.date, days: i+1, exitPrice, returnPct, note: `High ${d.high} -> TP ${sig.tp}` };
    }
    if (hitSL) {
      const exitPrice = sig.sl;
      const returnPct = (exitPrice - sig.entry) / sig.entry;
      return { outcome: "SL_HIT" as const, hitDate: d.date, days: i+1, exitPrice, returnPct, note: `Low ${d.low} -> SL ${sig.sl}` };
    }
  }
  if (slice.length < TIMEOUT_DAYS) {
    return { outcome: "OPEN" as const, hitDate: null, days: slice.length, exitPrice: null, returnPct: null, note: "Belum cukup data" };
  }
  const last = slice[slice.length-1];
  const exitPrice = last.close;
  const returnPct = (exitPrice - sig.entry) / sig.entry;
  return { outcome: "TIMEOUT" as const, hitDate: last.date, days: TIMEOUT_DAYS, exitPrice, returnPct, note: `Timeout close ${exitPrice}` };
}

export async function GET() {
  const signals = (await redis.get("tekb:evaluasi")) as Signal[] || [];
  const results = [];
  for (const sig of signals) {
    const ohlc = await fetchOHLC(sig.kode, sig.tanggal);
    const evalRes = evaluateSignal(sig, ohlc);
    results.push({...sig,...evalRes });
  }
  const closed = results.filter(r=> ["TP_HIT","SL_HIT","TIMEOUT"].includes(r.outcome));
  const tp = results.filter(r=> r.outcome==="TP_HIT").length;
  const sl = results.filter(r=> r.outcome==="SL_HIT").length;
  const timeout = results.filter(r=> r.outcome==="TIMEOUT").length;
  const amb = results.filter(r=> r.outcome==="AMBIGUOUS_INTRABAR").length;
  const open = results.filter(r=> r.outcome==="OPEN").length;
  const winRate = closed.length? (tp / closed.length * 100) : 0;
  return NextResponse.json({
    summary: {
      total: results.length, tp, sl, timeout, ambiguous: amb, open,
      closed: closed.length, winRate: Number(winRate.toFixed(2)),
      formula: "WinRate = TP / (TP+SL+TIMEOUT) | Return = (Exit-Entry)/Entry"
    },
    results: results.sort((a,b)=> b.tanggal.localeCompare(a.tanggal))
  });
}