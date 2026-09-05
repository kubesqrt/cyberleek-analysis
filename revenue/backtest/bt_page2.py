"""Render the strategy-search / sizing / capture / long-hold results into a static page section (appended to the backtest page)."""
import json, math, os
S = json.load(open("bt_results_search.json")); Z = json.load(open("bt_results_sizing.json")); C = json.load(open("bt_results_capture.json")); L = json.load(open("bt_results_longhold.json"))
K = json.load(open("bt_results_combo.json")) if os.path.exists("bt_results_combo.json") else None
pct = lambda v, d=1: "—" if v is None else f"{v*100:+.{d}f}%"
num = lambda v, d=2: "—" if v is None else f"{v:.{d}f}"
def cls(v): return "pos" if (v or 0) > 0 else ("neg" if (v or 0) < 0 else "")

def table(rows, cols, key_label="label"):
    head = "".join(f"<th>{t}</th>" for _, t, _ in cols)
    body = ""
    for r in rows:
        cells = ""
        for k, _, fmt in cols:
            v = r.get(k)
            if fmt == "pct": cells += f'<td class="num {cls(v)}">{pct(v)}</td>'
            elif fmt == "pct0": cells += f'<td class="num">{pct(v,0)}</td>'
            elif fmt == "num": cells += f'<td class="num">{num(v)}</td>'
            elif fmt == "int": cells += f'<td class="num">{"—" if v is None else int(v)}</td>'
            else: cells += f'<td class="l">{v}</td>'
        body += f'<tr><td class="l">{r.get(key_label)}</td>{cells}</tr>'
    return f'<div class="card wrap"><table><thead><tr><th class="l">Strategy</th>{head}</tr></thead><tbody>{body}</tbody></table></div>'

strat = [r for r in S["table"] if r["family"] != "bench"]
bench = [r for r in S["table"] if r["family"] == "bench"]
top = sorted(strat, key=lambda r: -(r["sharpe"] or -9))
cols_s = [("family", "Family", "txt"), ("total", "Total", "pct"), ("cagr", "CAGR", "pct"), ("sharpe", "Sharpe", "num"), ("maxdd", "Max DD", "pct"), ("exposure", "Exposure", "pct0"),
          ("n_trades", "Trades", "int"), ("hit", "Hit", "pct0"), ("sharpe_h1", "Sharpe 1st half", "num"), ("sharpe_h2", "Sharpe 2nd half", "num")]
h1top = sorted(strat, key=lambda r: -(r["sharpe_h1"] or -9))[:10]
import statistics
fam = {}
for r in strat: fam.setdefault(r["family"], []).append(r)
fam_rows = [{"label": f, "n": len(v), "med_sharpe": statistics.median([x["sharpe"] for x in v if x["sharpe"] is not None]), "best": max(x["sharpe"] for x in v if x["sharpe"] is not None),
             "med_dd": statistics.median([x["maxdd"] for x in v]), "med_total": statistics.median([x["total"] for x in v]), "share_pos": sum(1 for x in v if x["total"] > 0) / len(v)} for f, v in sorted(fam.items())]
sh = [r["sharpe"] for r in strat if r["sharpe"] is not None]

html = f"""
<h2 id="search">Strategy search — {S['n']} revenue strategies ranked by Sharpe</h2>
<div class="verdict">Multiple-testing check: with {S['n']} strategies over {S['T']} days, the <b>best Sharpe you'd expect from pure noise is ≈ {S['noise_max_sharpe']:.2f}</b>. The best full-sample Sharpe found is {max(sh):.2f} — so no single "winner" is distinguishable from luck on Sharpe alone. What <i>is</i> evidence: (1) the breakout family is positive almost everywhere (median Sharpe {statistics.median([x['sharpe'] for x in fam['A breakout']]):.2f} across {len(fam['A breakout'])} variants), (2) in the split-sample test the first-half top-10 kept a second-half Sharpe of {statistics.mean([r['sharpe_h2'] for r in h1top]):.2f} on average while the median strategy fell to {statistics.median([r['sharpe_h2'] for r in strat if r['sharpe_h2'] is not None]):.2f} and BTC to {[b for b in bench if b['label']=='BTC'][0]['sharpe_h2']:.2f}, and (3) the exits that survived the holdout are the revenue-slowdown ones — the fixed 28-day holds that topped the first half collapsed in the second.</div>
<div class="tiles"><div class="tile"><div class="v">{statistics.median(sh):.2f}</div><div class="l">median Sharpe, all strategies</div></div><div class="tile"><div class="v">{sum(1 for r in strat if r['total']>0)/len(strat)*100:.0f}%</div><div class="l">strategies with positive total return</div></div><div class="tile"><div class="v">{sum(1 for r in strat if (r['sharpe'] or -9) > [b for b in bench if b['label']=='BTC'][0]['sharpe'])/len(strat)*100:.0f}%</div><div class="l">beat BTC's Sharpe (0.41)</div></div><div class="tile"><div class="v">{S['noise_max_sharpe']:.2f}</div><div class="l">noise-max Sharpe for {S['n']} tries</div></div></div>
<h4>By family</h4>
{table(fam_rows, [("n","n","int"),("med_sharpe","Median Sharpe","num"),("best","Best Sharpe","num"),("med_dd","Median max DD","pct"),("med_total","Median total","pct"),("share_pos","Share positive","pct0")])}
<h4>Split-sample holdout — top 10 by first-half Sharpe, and what they did in the second half</h4>
{table(h1top, [("sharpe_h1","Sharpe 1st half","num"),("ret_h1","Return 1st half","pct"),("sharpe_h2","Sharpe 2nd half","num"),("ret_h2","Return 2nd half","pct"),("total","Full total","pct")])}
<h4>All {len(strat)} strategies, ranked by full-sample Sharpe (benchmarks at the bottom)</h4>
{table(top + bench, cols_s)}
<h4>Leverage overlay on the top 5 (daily rebalanced, 10%/yr funding on the borrowed portion)</h4>
{table([{"label": f"{r['label']} @ {r['L']}x", **r} for r in S['leverage']], [("total","Total","pct"),("sharpe","Sharpe","num"),("maxdd","Max DD","pct")])}
<p class="note">Constant leverage leaves Sharpe roughly unchanged (minus funding) and converts return into drawdown: every top strategy at 3× spends time down 85–98%. It is not a free multiplier on a 60–75%-vol strategy.</p>

<h2 id="sizing">Position sizing on the best breakout rule</h2>
<p class="note">Same signal and exit (2× / 8-week high → exit on revenue slowdown), 10 slots, but each position's size scaled 0.25×–2× by a cross-sectional rank at entry.</p>
{table(sorted(Z['sizing'], key=lambda r: -(r['sharpe'] or -9)), [("total","Total","pct"),("sharpe","Sharpe","num"),("maxdd","Max DD","pct"),("exposure","Exposure","pct0"),("hit","Hit","pct0"),("sharpe_h1","Sharpe 1st half","num"),("sharpe_h2","Sharpe 2nd half","num")], key_label="sizing")}
<h4>Leverage: constant vs volatility-targeted (cap 3×)</h4>
{table([{"label": f"{r['strategy']} · {r['overlay']}", **r} for r in Z['leverage']], [("total","Total","pct"),("sharpe","Sharpe","num"),("maxdd","Max DD","pct"),("avg_lev","Avg leverage","num")])}
{("<h4>Joint test — combining the survivors</h4>" + table([{"label": k, **v} for k, v in K["stats"].items()], [("total","Total","pct"),("sharpe","Sharpe","num"),("maxdd","Max DD","pct"),("exposure","Exposure","pct0"),("n","Trades","int"),("hit","Hit","pct0"),("sharpe_h1","Sharpe 1st half","num"),("sharpe_h2","Sharpe 2nd half","num"),("ytd2026","2026 YTD","pct")])) if K else ""}

<h2 id="capture">Revenue-to-token (holders revenue) variants</h2>
{table(list(C['stats'].values()), [("total","Total","pct"),("sharpe","Sharpe","num"),("maxdd","Max DD","pct"),("exposure","Exposure","pct0"),("n_trades","Trades","int"),("avg_ret","Avg trade","pct"),("alpha_vs_matched","Alpha vs matched","pct")])}
<p class="note">Signalling on holders revenue alone is worse (fewer, lumpier signals); using capture to <i>size</i> positions is better on every axis. Event study: 4 weeks after a breakout, tokens paying 75%+ of revenue to holders showed +14.6% excess vs +5.2% for tokens paying none (t≈1.9 vs 1.4).</p>

<h2 id="longhold">Long-term holds on sustained revenue ramps</h2>
{table(list(L['stats'].values()), [("total","Total","pct"),("cagr","CAGR","pct"),("sharpe","Sharpe","num"),("maxdd","Max DD","pct"),("n_trades","Trades","int"),("hit","Hit","pct0"),("avg_days","Avg days","num"),("exposure","Exposure","pct0"),("alpha_vs_matched","Alpha vs matched","pct")])}
<p class="note">Every long-hold variant lost money and under-performed even the −40% equal-weight universe. Entries clustered at the December 2024 cycle top (SKY, AERO, JUP, CAKE all signalled within days of each other and are down 25–80% since) and the revenue-breakdown exit only fires after price has already collapsed: at cycle turns, monthly revenue is a <i>lagging</i> indicator. The instant-scale launches (PUMP, LIT, EDGE) never signalled because the rules require 90 days of history — a "new listing with material revenue in its first month" rule would be needed to catch those, and that is a different bet. HYPE was the one clean catch (signalled 26 Jun 2025 at $37.6, +126% since).</p>
"""
open("search_section.html", "w").write(html)
print("wrote search_section.html", len(html))
