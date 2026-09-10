import { Redis } from "@upstash/redis";
import { NextResponse } from "next/server";

export const runtime = "edge";
const redis = Redis.fromEnv();

const TIMEOUT_BARS = 78; // LOCK: 78 bars, bukan klaim durasi universal
const TIMEFRAME = "5m";
const EVALUATOR_VERSION = "v2-5m-78bars-yahoo-validation";

type Signal = {
  signalId?: string;
  tanggal: string; // YYYY-MM-DD
  jam?: string; // HH:mm
  kode: string;
  entry: number;
  sl: number;
  tp: number;
  action: "BUY" | "SELL";
  model?: string;
};

// Yahoo 5m - hanya untuk validasi engine, max 7 hari history
async function fetchOHLC5m(kode: string, fromDateTime: Date) {
  const symbol = `${kode}.JK`;
  const period1 = Math.floor(fromDateTime.getTime() / 1000);
  // 78 bars 5m = 390 menit = ~6.5 jam, ambil buffer 2 hari biar aman
  const period2 = period1 + 2 * 24 * 3600;
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?period1=${period1}&period2=${period2}&interval=5m&includeAdjustedClose=true`;

  try {
    const res = await fetch(url, { headers: { "User-Agent": "Mozilla/5.0" } });
    const json = await res.json();
    const result = json.chart?.result?.[0];
    if (!result) return { candles: [], meta: { provider: "yahoo", symbol, timeframe: TIMEFRAME, error: "no result" } };

    const timestamps = result.timestamp || [];
    const quote = result.indicators?.quote?.[0];
    const highs = quote?.high || [];
    const lows = quote?.low || [];
    const closes = quote?.close || [];
    const opens = quote?.open || [];

    const candles = timestamps.map((t: number, i: number) => ({
      timestamp: t * 1000,
      dateTime: new Date(t * 1000).toISOString(),
      date: new Date(t * 1000).toISOString().slice(0, 10),
      time: new Date(t * 1000).toISOString().slice(11, 16),
      open: opens[i],
      high: highs[i],
      low: lows[i],
      close: closes[i],
    })).filter((d: any) => d.high!= null && d.low!= null);

    return {
      candles,
      meta: {
        provider: "yahoo",
        symbol,
        timeframe: TIMEFRAME,
        data_start: candles[0]?.dateTime || null,
        data_end: candles[candles.length - 1]?.dateTime || null,
        total_bars_fetched: candles.length,
      }
    };
  } catch (e: any) {
    return { candles: [], meta: { provider: "yahoo", symbol, timeframe: TIMEFRAME, error: e.message } };
  }
}

function evaluateSignal5m(sig: Signal, ohlcData: any) {
  const { candles, meta } = ohlcData;

  // SIGNAL TIMESTAMP = tanggal + jam
  const signalTimeStr = `${sig.tanggal}T${sig.jam || "00:00"}:00`;
  const signalTimestamp = new Date(signalTimeStr).getTime();

  // START = first 5m bar strictly AFTER signal timestamp
  const startIdx = candles.findIndex((d: any) => d.timestamp > signalTimestamp);
  const slice = startIdx >= 0? candles.slice(startIdx, startIdx + TIMEOUT_BARS) : [];

  const provenance = {
    provider: meta.provider,
    symbol: meta.symbol,
    timeframe: TIMEFRAME,
    evaluator_version: EVALUATOR_VERSION,
    signal_timestamp: new Date(signalTimestamp).toISOString(),
    signal_timestamp_raw: `${sig.tanggal} ${sig.jam || "00:00"}`,
    first_eval_timestamp: slice[0]?.dateTime || null,
    last_eval_timestamp: slice[slice.length - 1]?.dateTime || null,
    bars_evaluated: slice.length,
    timeout_bars: TIMEOUT_BARS,
    data_start: meta.data_start,
    data_end: meta.data_end,
    total_bars_fetched: meta.total_bars_fetched,
  };

  if (slice.length === 0) {
    return {
      outcome: "OPEN" as const,
      hitDate: null,
      hitTime: null,
      days: 0,
      bars: 0,
      exitPrice: null,
      returnPct: null,
      note: `Belum ada candle 5m setelah signal ${sig.jam || "00:00"} - Yahoo 5m hanya 7 hari`,
      provenance,
    };
  }

  for (let i = 0; i < slice.length; i++) {
    const d = slice[i];
    let hitTP = false, hitSL = false;

    if (sig.action === "BUY") {
      hitTP = d.high >= sig.tp;
      hitSL = d.low <= sig.sl;
    } else { // SELL
      hitTP = d.low <= sig.tp;
      hitSL = d.high >= sig.sl;
    }

    // AMBIGUOUS jika TP & SL kena di bar yang SAMA - tidak boleh tebak urutan
    if (hitTP && hitSL) {
      return {
        outcome: "AMBIGUOUS_INTRABAR" as const,
        hitDate: d.date,
        hitTime: d.time,
        days: i + 1,
        bars: i + 1,
        exitPrice: null,
        returnPct: null,
        note: `AMBIGUOUS 5m ${d.date} ${d.time}: H=${d.high} L=${d.low} vs TP=${sig.tp} SL=${sig.sl}`,
        provenance: {...provenance, hit_bar: d, hit_bar_index: i },
      };
    }
    if (hitTP) {
      const exitPrice = sig.tp;
      const returnPct = sig.action === "BUY"? (exitPrice - sig.entry) / sig.entry : (sig.entry - exitPrice) / sig.entry;
      return {
        outcome: "TP_HIT" as const,
        hitDate: d.date,
        hitTime: d.time,
        days: i + 1,
        bars: i + 1,
        exitPrice,
        returnPct,
        note: `${sig.action} TP_HIT 5m ${d.date} ${d.time} ${sig.action === "BUY"? `H=${d.high}` : `L=${d.low}`} >= TP ${sig.tp}`,
        provenance: {...provenance, hit_bar: d, hit_bar_index: i },
      };
    }
    if (hitSL) {
      const exitPrice = sig.sl;
      const returnPct = sig.action === "BUY"? (exitPrice - sig.entry) / sig.entry : (sig.entry - exitPrice) / sig.entry;
      return {
        outcome: "SL_HIT" as const,
        hitDate: d.date,
        hitTime: d.time,
        days: i + 1,
        bars: i + 1,
        exitPrice,
        returnPct,
        note: `${sig.action} SL_HIT 5m ${d.date} ${d.time} ${sig.action === "BUY"? `L=${d.low}` : `H=${d.high}`} vs SL ${sig.sl}`,
        provenance: {...provenance, hit_bar: d, hit_bar_index: i },
      };
    }
  }

  if (slice.length < TIMEOUT_BARS) {
    return {
      outcome: "OPEN" as const,
      hitDate: null,
      hitTime: null,
      days: slice.length,
      bars: slice.length,
      exitPrice: null,
      returnPct: null,
      note: `OPEN: baru ${slice.length}/${TIMEOUT_BARS} bars 5m`,
      provenance,
    };
  }

  // TIMEOUT
  const last = slice[slice.length - 1];
  const exitPrice = last.close;
  const returnPct = sig.action === "BUY"? (exitPrice - sig.entry) / sig.entry : (sig.entry - exitPrice) / sig.entry;
  return {
    outcome: "TIMEOUT" as const,
    hitDate: last.date,
    hitTime: last.time,
    days: TIMEOUT_BARS,
    bars: TIMEOUT_BARS,
    exitPrice,
    returnPct,
    note: `TIMEOUT 78 bars close ${exitPrice} return ${(returnPct * 100).toFixed(2)}%`,
    provenance,
  };
}

export async function GET() {
  const signals = (await redis.get("evaluasi:signals")) as Signal[] || [];
  const results = [];

  for (const sig of signals) {
    const signalTime = new Date(`${sig.tanggal}T${sig.jam || "00:00"}:00`);
    const ohlcData = await fetchOHLC5m(sig.kode, signalTime);
    const evalRes = evaluateSignal5m(sig, ohlcData);
    const signalId = sig.signalId || `${sig.kode}-${sig.tanggal}-${sig.jam || '00:00'}-${sig.action}`;
    results.push({...sig, signalId,...evalRes });
  }

  const closed = results.filter(r => ["TP_HIT", "SL_HIT", "TIMEOUT"].includes(r.outcome));
  const tp = results.filter(r => r.outcome === "TP_HIT").length;
  const sl = results.filter(r => r.outcome === "SL_HIT").length;
  const timeout = results.filter(r => r.outcome === "TIMEOUT").length;
  const amb = results.filter(r => r.outcome === "AMBIGUOUS_INTRABAR").length;
  const open = results.filter(r => r.outcome === "OPEN").length;
  const winRate = closed.length? (tp / closed.length * 100) : 0;
  const avgReturn = closed.length? closed.reduce((a, b) => a + (b.returnPct || 0), 0) / closed.length : 0;

  return NextResponse.json({
    summary: {
      total: results.length,
      tp, sl, timeout, ambiguous: amb, open, closed,
      winRate: Number(winRate.toFixed(2)),
      avgReturn: Number((avgReturn * 100).toFixed(2)),
      timeframe: TIMEFRAME,
      timeout_bars: TIMEOUT_BARS,
      evaluator_version: EVALUATOR_VERSION,
      engine_type: "V2_ENGINE_VALIDATION - Yahoo 5m, bukan historical track record",
      formula: "BUY: TP=High>=TP SL=Low<=SL | SELL: TP=Low<=TP SL=High>=SL | FIRST HIT 5m | TIMEOUT=Close bar 78"
    },
    results: results.sort((a, b) => {
      const ta = `${a.tanggal} ${a.jam || "00:00"}`;
      const tb = `${b.tanggal} ${b.jam || "00:00"}`;
      return tb.localeCompare(ta);
    })
  });
}