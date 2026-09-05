"""Build the backtest universe: protocols with a token (gecko_id) and material revenue history."""
import json, re, urllib.request
H = {"User-Agent": "Mozilla/5.0"}
get = lambda u: json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=120).read())
rev = get("https://api.llama.fi/overview/fees?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true&dataType=dailyRevenue")
lite = get("https://api.llama.fi/lite/protocols2?b=2")
pp = {p["id"]: p for p in lite["parentProtocols"]}
slug = lambda n: re.sub(r"[^a-z0-9]+", "-", n.lower()).strip("-")
byslug = {slug(p["name"]): p for p in lite["protocols"]}
ent = {}
for p in rev["protocols"]:
    if p.get("protocolType") == "chain": continue
    par = p.get("parentProtocol"); key = par or "solo#" + p["slug"]
    lp = byslug.get(p["slug"])
    e = ent.setdefault(key, {"key": key, "name": pp[par]["name"] if par in pp else p["name"],
        "gecko": (pp[par].get("gecko_id") if par in pp else (lp or {}).get("gecko_id")),
        "symbol": (pp[par].get("symbol") if par in pp else (lp or {}).get("symbol")),
        "slugs": [], "r1y": 0, "rall": 0, "r30": 0})
    e["slugs"].append(p["slug"]); e["r1y"] += p.get("total1y") or 0; e["rall"] += p.get("totalAllTime") or 0; e["r30"] += p.get("total30d") or 0
U = [e for e in ent.values() if e["gecko"] and e["gecko"] != "-" and (e["r1y"] >= 500_000 or e["rall"] >= 2_000_000)]
U.sort(key=lambda e: -e["r1y"])
json.dump(U, open("bt_universe.json", "w"))
print("universe:", len(U), "child slugs:", sum(len(e["slugs"]) for e in U))
