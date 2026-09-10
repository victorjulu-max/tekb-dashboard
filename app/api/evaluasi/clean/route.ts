import { Redis } from "@upstash/redis";
import { NextResponse } from "next/server";
export const runtime = "edge";
const redis = Redis.fromEnv();
export async function POST() {
  const all = (await redis.get("tekb:evaluasi")) as any[] || [];
  const sisa = all.filter((r:any) => r.tanggal !== "2025-08-01");
  await redis.set("tekb:evaluasi", sisa);
  return NextResponse.json({ ok: true, sebelum: all.length, sesudah: sisa.length });
}