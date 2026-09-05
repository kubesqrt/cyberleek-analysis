import json, urllib.request, time, os
U = json.load(open("bt_universe.json"))
os.makedirs("bt_hrev", exist_ok=True)
H = {"User-Agent": "Mozilla/5.0"}
slugs = [s for e in U for s in e["slugs"]]
done = fail = 0
for i, s in enumerate(slugs):
    f = f"bt_hrev/{s}.json"
    if os.path.exists(f):
        continue
    for k in range(3):
        try:
            d = json.loads(urllib.request.urlopen(urllib.request.Request(
                f"https://api.llama.fi/summary/fees/{s}?dataType=dailyHoldersRevenue", headers=H), timeout=60).read())
            json.dump(d.get("totalDataChart") or [], open(f, "w"))
            done += 1
            break
        except Exception as e:
            if k == 2:
                fail += 1
                json.dump([], open(f, "w"))
            time.sleep(2 * (k + 1))
    time.sleep(0.25)
    if i % 50 == 0:
        print(i, "/", len(slugs), flush=True)
print("holders-revenue fetch done:", done, "failed:", fail, flush=True)
