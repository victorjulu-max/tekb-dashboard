import { Redis } from "@upstash/redis";
import { NextResponse } from "next/server";

export const runtime = "edge";
const redis = Redis.fromEnv();

export async function GET() {
  try {
    const data = (await redis.get("tekb:evaluasi")) as any[] || [];
    return NextResponse.json(data);
  } catch {
    return NextResponse.json([]);
  }
}

export async function POST(req: Request) {
  try {
    const { rows } = await req.json();
    const existing = (await redis.get("tekb:evaluasi")) as any[] || [];
    let tambah = 0;
    for (const r of rows) {
      const ada = existing.some((x:any) => x.tanggal === r.tanggal && x.kode === r.kode);
      if (!ada) {
        existing.push(r);
        tambah++;
      }
    }
    await redis.set("tekb:evaluasi", existing);
    return NextResponse.json({ ok: true, tambah, total: existing.length });
  } catch (e:any) {
    return NextResponse.json({ ok: false, error: e.message }, { status: 500 });
  }
}