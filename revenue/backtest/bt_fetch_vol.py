"""Daily token volume + market cap history from CoinGecko (public API, rate-limited)."""
import json, urllib.request, time, os
U = json.load(open("bt_universe.json"))
os.makedirs("bt_vol", exist_ok=True)
H = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
ids = sorted({e["gecko"] for e in U})
ok = fail = 0
for i, g in enumerate(ids):
    f = f"bt_vol/{g}.json"
    if os.path.exists(f): continue
    url = f"https://api.coingecko.com/api/v3/coins/{g}/market_chart?vs_currency=usd&days=365"
    got = None
    for k in range(6):
        try:
            got = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=60).read()); break
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(15 + 10 * k); continue
            if e.code == 404: got = {}; break
            time.sleep(5)
        except Exception: time.sleep(5)
    if got is None: fail += 1; got = {}
    else: ok += 1
    json.dump({"volumes": got.get("total_volumes", []), "market_caps": got.get("market_caps", [])}, open(f, "w"))
    time.sleep(2.6)
    if i % 20 == 0: print(i, "/", len(ids), flush=True)
print("volume fetch done:", ok, "failed:", fail, flush=True)
