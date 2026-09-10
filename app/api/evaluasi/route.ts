import { NextRequest, NextResponse } from "next/server";
import { Redis } from "@upstash/redis";

const redis = Redis.fromEnv();
const KEY = "evaluasi:signals";

export async function GET() {
  try {
    const data = await redis.get(KEY);
    return NextResponse.json({ rows: data || [] });
  } catch (e: any) {
    return NextResponse.json({ rows: [], error: e.message }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const rows = body.rows || body; // support langsung array juga
    if (!Array.isArray(rows)) {
      return NextResponse.json({ error: "rows harus array" }, { status: 400 });
    }
    const existing = (await redis.get(KEY)) as any[] || [];
    const map = new Map();
    existing.forEach((r: any) => map.set(r.signalId || `${r.kode}-${r.tanggal}-${r.action}`, r));
    let tambah = 0;
    rows.forEach((r: any) => {
      const key = r.signalId || `${r.kode}-${r.tanggal}-${r.action}`;
      if (!map.has(key)) tambah++;
      map.set(key, r);
    });
    const merged = Array.from(map.values());
    await redis.set(KEY, merged);
    return NextResponse.json({ ok: true, tambah, total: merged.length });
  } catch (e: any) {
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}

export async function DELETE(req: NextRequest) {
  try {
    const body = await req.json().catch(() => ({}));
    const ids = body.signalIds || (body.signalId ? [body.signalId] : null);
    
    if (!ids) {
      // kalau tanpa body = hapus semua (reset bersih)
      await redis.set(KEY, []);
      return NextResponse.json({ ok: true, total: 0, message: "Semua dihapus - track record bersih" });
    }

    const existing = (await redis.get(KEY)) as any[] || [];
    const filtered = existing.filter((r: any) => !ids.includes(r.signalId));
    await redis.set(KEY, filtered);
    return NextResponse.json({ ok: true, hapus: existing.length - filtered.length, total: filtered.length });
  } catch (e: any) {
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}