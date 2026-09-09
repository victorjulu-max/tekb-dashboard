export const dynamic = 'force-dynamic';

export async function GET() {
  const fallbackPrices = { BBCA: 9750, TLKM: 3350 };
  let livePrices = {...fallbackPrices };
  try {
    const [bbcaRes, tlkmRes] = await Promise.all([
      fetch('https://query1.finance.yahoo.com/v8/finance/chart/BBCA.JK', { next: { revalidate: 60 } }).then(r=>r.json()).catch(()=>null),
      fetch('https://query1.finance.yahoo.com/v8/finance/chart/TLKM.JK', { next: { revalidate: 60 } }).then(r=>r.json()).catch(()=>null),
    ]);
    if (bbcaRes?.chart?.result?.[0]?.meta?.regularMarketPrice) livePrices.BBCA = bbcaRes.chart.result[0].meta.regularMarketPrice;
    if (tlkmRes?.chart?.result?.[0]?.meta?.regularMarketPrice) livePrices.TLKM = tlkmRes.chart.result[0].meta.regularMarketPrice;
  } catch (e) {}

  return Response.json({
    status: "GOLDEN v1.4 LIVE P&L",
    engine: "TEKBPipeline",
    v14_golden: true,
    hygiene_order_locked: true,
    live_prices: livePrices,
    fetched_at: new Date().toISOString(),

    // 🔒 RESEARCH BATCH CONFIG v1.0 FINAL V3 - LOCKED
    research_batch_config: {
      version: "RESEARCH BATCH CONFIG v1.0 FINAL V3 - LOCKED",
      batch_id: "TEKB_5m_2024_IS_001",
      hash: "575bc4d31848d13c573f04080f5b8fd0dc236a75bd069bebffc1eb46f0b48015",
      short_hash: "575bc4d3",
      total_candidates: 144,
      breakdown: "6 features x 6 windows x 4 models = 144",
      locked: true,
      locked_at_commit: "3798212",
      file: "tekb_core/research_batch_config_v1_locked.py"
    },

    scan: [
      { code: "BBCA", rv: 2.8, baseline: 1.2, signal: 1.6, action: "STRONG BUY", last: livePrices.BBCA },
      { code: "TLKM", rv: 3.1, baseline: 1.3, signal: 1.8, action: "STRONG BUY", last: livePrices.TLKM }
    ]
  });
}