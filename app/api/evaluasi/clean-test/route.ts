import { Redis } from "@upstash/redis";
import { NextResponse } from "next/server";
const redis = Redis.fromEnv();
const KEY = "evaluasi:signals";
export async function GET() {
  const existing = (await redis.get(KEY)) as any[] || [];
  const filtered = existing.filter((r:any) => r.signalId !== "BBCA-2026-08-01-09:15-BUY");
  await redis.set(KEY, filtered);
  return NextResponse.json({ ok:true, before: existing.length, after: filtered.length, message: `Bersih! ${existing.length} -> ${filtered.length}` });
}