import json, urllib.request, time, os
U = json.load(open("bt_universe.json"))
os.makedirs("bt_px", exist_ok=True)
H = {"User-Agent": "Mozilla/5.0"}
now = int(time.time())
ids = sorted({e["gecko"] for e in U}) + ["bitcoin", "ethereum"]
done = fail = 0
for i, g in enumerate(ids):
    f = f"bt_px/{g}.json"
    if os.path.exists(f):
        continue
    pts = {}
    ok = True
    for start in (now - 760 * 86400, now - 380 * 86400):
        url = f"https://coins.llama.fi/chart/coingecko:{g}?start={start}&span=380&period=1d"
        got = False
        for k in range(3):
            try:
                d = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=60).read())
                for p in (d.get("coins", {}).get(f"coingecko:{g}", {}).get("prices") or []):
                    pts[p["timestamp"]] = p["price"]
                got = True
                break
            except Exception:
                time.sleep(2 * (k + 1))
        ok = ok and got
        time.sleep(0.3)
    json.dump(sorted(pts.items()), open(f, "w"))
    done += 1 if ok else 0
    fail += 0 if ok else 1
    if i % 25 == 0:
        print(i, "/", len(ids), flush=True)
print("price fetch done:", done, "failed:", fail, flush=True)
