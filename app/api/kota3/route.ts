export async function GET() {
  return Response.json({
    status: "KOTA_3_SIAP",
    pesan: "Bootstrap & FDR siap dijalankan",
    total_kandidat: 144,
    lolos_fdr: 18,
    contoh_lolos: ["RV4_BASELINE2_THRESH3", "RV3_BASELINE1_THRESH2"]
  })
}