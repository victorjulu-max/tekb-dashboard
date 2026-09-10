fetch("https://tekb-dashboard.vercel.app/api/evaluasi",{
 method:"POST",
 headers:{"Content-Type":"application/json"},
 body: JSON.stringify({rows:[
  {tanggal:"2025-08-01", kode:"BBCA", action:"BUY", entry:9000, sl:8500, tp:9500, model:"TEST HISTORIS"},
  {tanggal:"2025-08-01", kode:"TLKM", action:"BUY", entry:3000, sl:2800, tp:3300, model:"TEST HISTORIS"}
 ]})
}).then(r=>r.json()).then(console.log)