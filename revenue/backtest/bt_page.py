"""Render bt_results.json -> static HTML results page (inline SVG, no deps)."""
import json, math, sys
R = json.load(open("bt_results.json"))
OUT = sys.argv[1] if len(sys.argv) > 1 else "backtest.html"

SHOW = [  # label, display name, color slot
    ("K1.5_N28_slow", "Revenue breakout (1.5×, 4-wk high) → exit when rev slows", "--s1"),
    ("K2.0_N56_slow", "Revenue breakout (2×, 8-wk high) → exit when rev slows", "--s2"),
    ("PRICE breakout control", "Price breakout control (same rules on price)", "--s3"),
    ("EW universe", "Equal-weight universe (buy & hold)", "--s4"),
    ("BTC", "BTC", "--s5"),
    ("ETH", "ETH", "--s6"),
]
pct = lambda v, d=1: "—" if v is None else f"{v*100:+.{d}f}%"
num = lambda v, d=2: "—" if v is None else f"{v:.{d}f}"

def curve_svg(curves, keys):
    W, H, pl, pr, pt, pb = 960, 340, 56, 12, 10, 28
    iw, ih = W - pl - pr, H - pt - pb
    series = {k: curves[k] for k in keys if k in curves}
    dates = sorted({d for s in series.values() for d, _ in s})
    di = {d: i for i, d in enumerate(dates)}
    allv = [v for s in series.values() for _, v in s if v > 0]
    lo, hi = min(allv), max(allv)
    lo, hi = math.log(lo) - 0.05, math.log(hi) + 0.05      # log scale
    x = lambda d: pl + iw * di[d] / max(1, len(dates) - 1)
    y = lambda v: pt + ih * (1 - (math.log(v) - lo) / (hi - lo))
    grid = lab = ""
    for g in (0.25, 0.5, 1, 2, 4, 8, 16):
        if lo <= math.log(g) <= hi:
            gy = y(g)
            grid += f'<line x1="{pl}" x2="{W-pr}" y1="{gy:.1f}" y2="{gy:.1f}" stroke="var(--grid)"/>'
            lab += f'<text x="{pl-6}" y="{gy+3:.1f}" text-anchor="end" font-size="10" fill="var(--muted)">{g}×</text>'
    paths = ""
    for k, name, col in SHOW:
        if k not in series: continue
        pts = " L".join(f"{x(d):.1f},{y(v):.1f}" for d, v in series[k] if v > 0)
        main = col in ("--s1", "--s2")
        sw = 2 if main else 1.5
        op = 1 if main else 0.85
        paths += f'<path d="M{pts}" fill="none" stroke="var({col})" stroke-width="{sw}" stroke-linejoin="round" opacity="{op}"/>'
    months = {}
    for d in dates:
        k = d[:7]
        months.setdefault(k, d)
    xl = ""
    for i, (k, d) in enumerate(sorted(months.items())):
        if i % 3 == 0:
            xl += f'<text x="{x(d):.1f}" y="{H-8}" font-size="10" fill="var(--muted)">{k}</text>'
    legend = "".join(f'<span><i style="background:var({col})"></i>{name}</span>' for k, name, col in SHOW if k in series)
    return f'<div class="legend">{legend}</div><svg viewBox="0 0 {W} {H}" width="100%" style="display:block">{grid}{lab}<line x1="{pl}" x2="{W-pr}" y1="{y(1):.1f}" y2="{y(1):.1f}" stroke="var(--border2)"/>{paths}{xl}</svg>'

def stats_table():
    cols = [("total", "Total"), ("cagr", "CAGR"), ("vol", "Vol"), ("sharpe", "Sharpe"), ("maxdd", "Max DD"),
            ("exposure", "Exposure"), ("matched_bench_total", "Exp-matched EW"), ("alpha_vs_matched", "Alpha vs matched"),
            ("n_trades", "Trades"), ("hit", "Hit"), ("avg_ret", "Avg trade"), ("med_ret", "Med trade"), ("avg_days", "Avg days")]
    order = [k for k, _, _ in SHOW] + [k for k in R["stats"] if k not in {x for x, _, _ in SHOW}]
    rows = ""
    for k in order:
        s = R["stats"].get(k)
        if not s: continue
        name = dict((a, b) for a, b, _ in SHOW).get(k, k)
        cells = ""
        for key, _ in cols:
            v = s.get(key)
            if key in ("total", "cagr", "vol", "maxdd", "exposure", "matched_bench_total", "alpha_vs_matched", "hit", "avg_ret", "med_ret"):
                c = "pos" if (v or 0) > 0 and key in ("total", "cagr", "alpha_vs_matched", "avg_ret", "med_ret") else ("neg" if (v or 0) < 0 and key in ("total", "cagr", "alpha_vs_matched", "avg_ret", "med_ret") else "")
                cells += f'<td class="num {c}">{pct(v, 0 if key in ("hit","exposure") else 1)}</td>'
            elif key == "sharpe": cells += f'<td class="num">{num(v)}</td>'
            elif key in ("n_trades",): cells += f'<td class="num">{"—" if v is None else int(v)}</td>'
            elif key == "avg_days": cells += f'<td class="num">{num(v,0)}</td>'
        rows += f'<tr><td class="l">{name}</td>{cells}</tr>'
    head = "".join(f"<th>{t}</th>" for _, t in cols)
    return f'<table><thead><tr><th class="l">Strategy</th>{head}</tr></thead><tbody>{rows}</tbody></table>'

def events_table():
    out = ""
    for tag, evs in R["events"].items():
        n = len(evs)
        rows = ""
        for h in (7, 28, 90):
            ok = lambda v: isinstance(v, (int, float)) and v == v
            r = [e[f"r{h}"] for e in evs if ok(e.get(f"r{h}"))]
            x = [e[f"x{h}"] for e in evs if ok(e.get(f"x{h}"))]
            if not x: continue
            mean = sum(x)/len(x); sd = (sum((v-mean)**2 for v in x)/max(1,len(x)-1))**0.5; t = mean/(sd/math.sqrt(len(x))) if sd>0 else float("nan")
            med = sorted(x)[len(x)//2]; rm = sum(r)/len(r); rmed = sorted(r)[len(r)//2]
            rows += (f'<tr><td class="l">+{h}d</td><td class="num">{len(x)}</td><td class="num {"pos" if rm>0 else "neg"}">{pct(rm)}</td><td class="num">{pct(rmed)}</td>'
                     f'<td class="num">{sum(1 for v in r if v>0)/len(r)*100:.0f}%</td><td class="num {"pos" if mean>0 else "neg"}"><b>{pct(mean)}</b></td><td class="num">{pct(med)}</td>'
                     f'<td class="num">{sum(1 for v in x if v>0)/len(x)*100:.0f}%</td><td class="num">{t:+.2f}</td></tr>')
        out += f'<h4>Breakout rule {tag.replace("_"," · ").replace("K","K=").replace("N","N=")} — {n} events</h4><table><thead><tr><th class="l">Horizon</th><th>n</th><th>Raw mean</th><th>Raw median</th><th>Raw hit</th><th>Excess vs EW mean</th><th>Excess median</th><th>Excess hit</th><th>t-stat</th></tr></thead><tbody>{rows}</tbody></table>'
    return out

R2 = json.load(open("bt_results2.json")) if __import__("os").path.exists("bt_results2.json") else None
FSHOW = [
    ("Revenue momentum (30d MoM, top quintile)", "--s1"),
    ("Value + growth combo (top quintile)", "--s2"),
    ("Revenue yield / value (cheapest quintile)", "--s3"),
    ("Price momentum control (30d, top quintile)", "--s4"),
    ("L/S spread: top − bottom revenue-momentum quintile", "--s5"),
    ("Bottom revenue-momentum quintile (avoid list)", "--s6"),
    ("EW universe", "--muted"),
]
def factor_curve_svg():
    W, H, pl, pr, pt, pb = 960, 340, 56, 12, 10, 28
    iw, ih = W - pl - pr, H - pt - pb
    series = {k: R2["curves"][k] for k, _ in FSHOW if k in R2["curves"]}
    dates = sorted({d for s in series.values() for d, _ in s}); di = {d: i for i, d in enumerate(dates)}
    allv = [v for s in series.values() for _, v in s if v > 0]
    lo, hi = math.log(min(allv)) - 0.05, math.log(max(allv)) + 0.05
    x = lambda d: pl + iw * di[d] / max(1, len(dates) - 1)
    y = lambda v: pt + ih * (1 - (math.log(v) - lo) / (hi - lo))
    grid = lab = ""
    for g in (0.125, 0.25, 0.5, 1, 2, 4):
        if lo <= math.log(g) <= hi:
            gy = y(g); grid += f'<line x1="{pl}" x2="{W-pr}" y1="{gy:.1f}" y2="{gy:.1f}" stroke="var(--grid)"/>'
            lab += f'<text x="{pl-6}" y="{gy+3:.1f}" text-anchor="end" font-size="10" fill="var(--muted)">{g}×</text>'
    paths = ""
    for k, col in FSHOW:
        if k not in series: continue
        pts = " L".join(f"{x(d):.1f},{y(v):.1f}" for d, v in series[k] if v > 0)
        paths += f'<path d="M{pts}" fill="none" stroke="var({col})" stroke-width="{2 if col in ("--s1","--s5") else 1.5}" stroke-linejoin="round"/>'
    months = {}
    for d in dates: months.setdefault(d[:7], d)
    xl = "".join(f'<text x="{x(d):.1f}" y="{H-8}" font-size="10" fill="var(--muted)">{k}</text>' for i, (k, d) in enumerate(sorted(months.items())) if i % 3 == 0)
    legend = "".join(f'<span><i style="background:var({col})"></i>{k}</span>' for k, col in FSHOW if k in series)
    return f'<div class="legend">{legend}</div><svg viewBox="0 0 {W} {H}" width="100%" style="display:block">{grid}{lab}<line x1="{pl}" x2="{W-pr}" y1="{y(1):.1f}" y2="{y(1):.1f}" stroke="var(--border2)"/>{paths}{xl}</svg>'

def factor_table():
    cols = [("total", "Total"), ("cagr", "CAGR"), ("vol", "Vol"), ("sharpe", "Sharpe"), ("maxdd", "Max DD"), ("exposure", "Exposure"), ("alpha_vs_EW", "Alpha vs EW")]
    rows = ""
    for k, _ in FSHOW + [("BTC", "")]:
        s = R2["stats"].get(k)
        if not s: continue
        cells = ""
        for key, _ in cols:
            v = s.get(key)
            if key == "sharpe": cells += f'<td class="num">{num(v)}</td>'
            else:
                c = "pos" if (v or 0) > 0 and key in ("total", "cagr", "alpha_vs_EW") else ("neg" if (v or 0) < 0 and key in ("total", "cagr", "alpha_vs_EW") else "")
                cells += f'<td class="num {c}">{pct(v, 0 if key == "exposure" else 1)}</td>'
        rows += f'<tr><td class="l">{k}</td>{cells}</tr>'
    return f'<table><thead><tr><th class="l">Portfolio</th>{"".join(f"<th>{t}</th>" for _, t in cols)}</tr></thead><tbody>{rows}</tbody></table>'

def factor_events_table():
    titles = {"fade": "Revenue FADE — rev7d < 0.5× its 8-week average and a 4-week low (candidate SELL signal)",
              "divergence": "DIVERGENCE — price down ≥20% in 30d while 30d revenue still growing (candidate BUY-the-dip)",
              "acceleration": "ACCELERATION turn — WoW revenue > +25% right after a flat/down week"}
    out = ""
    for tag, evs in R2["events"].items():
        rows = ""
        for h in (7, 28, 90):
            ok = lambda v: isinstance(v, (int, float)) and v == v
            r = [e[f"r{h}"] for e in evs if ok(e.get(f"r{h}"))]; x = [e[f"x{h}"] for e in evs if ok(e.get(f"x{h}"))]
            if not x: continue
            mean = sum(x)/len(x); sd = (sum((v-mean)**2 for v in x)/max(1,len(x)-1))**0.5; t = mean/(sd/math.sqrt(len(x))) if sd>0 else float("nan")
            rows += (f'<tr><td class="l">+{h}d</td><td class="num">{len(x)}</td><td class="num">{pct(sum(r)/len(r))}</td><td class="num">{pct(sorted(r)[len(r)//2])}</td>'
                     f'<td class="num {"pos" if mean>0 else "neg"}"><b>{pct(mean)}</b></td><td class="num">{pct(sorted(x)[len(x)//2])}</td><td class="num">{sum(1 for v in x if v>0)/len(x)*100:.0f}%</td><td class="num">{t:+.2f}</td></tr>')
        out += f'<h4>{titles.get(tag, tag)} — {len(evs)} events</h4><table><thead><tr><th class="l">Horizon</th><th>n</th><th>Raw mean</th><th>Raw median</th><th>Excess vs EW mean</th><th>Excess median</th><th>Excess hit</th><th>t-stat</th></tr></thead><tbody>{rows}</tbody></table>'
    return out

def trades_table(k="K1.5_N28_slow"):
    tr = R["trades"].get(k, [])
    tr = sorted(tr, key=lambda t: t["exit"], reverse=True)[:40]
    rows = "".join(f'<tr><td class="l">{t["sym"]}</td><td>{t["entry"]}</td><td>{t["exit"]}</td><td class="num">{t["days"]}</td><td class="num {"pos" if t["ret"]>0 else "neg"}">{pct(t["ret"])}</td></tr>' for t in tr)
    return f'<table><thead><tr><th class="l">Token</th><th>Entry</th><th>Exit</th><th>Days</th><th>Return</th></tr></thead><tbody>{rows}</tbody></table>'

html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Revenue Breakout Backtest — Alt Analysis</title>
<style>
:root{{color-scheme:dark;--bg:#0d1117;--panel:#161b22;--panel2:#1c2129;--border:#21262d;--border2:#30363d;--ink:#e6edf3;--ink2:#9198a1;--muted:#6e7681;--grid:#21262d;
--s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--s5:#d55181;--s6:#9085e9;--up:#3fb950;--down:#f85149}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.55 "Segoe UI",system-ui,sans-serif}}
main{{max-width:1180px;margin:0 auto;padding:1.1rem 1rem 4rem}} a{{color:var(--s1);text-decoration:none}} a:hover{{text-decoration:underline}}
h1{{font-size:1.35rem;margin:0}} h2{{font-size:1.05rem;margin:1.6rem 0 .5rem}} h4{{margin:1rem 0 .3rem;font-size:.85rem;color:var(--ink2)}}
.sub{{color:var(--ink2);font-size:.85rem;margin:.15rem 0 0}}
.card{{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:.8rem 1rem}}
.legend{{display:flex;gap:1rem;flex-wrap:wrap;font-size:.74rem;color:var(--ink2);margin:0 0 .4rem}} .legend i{{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px;vertical-align:-1px}}
table{{border-collapse:collapse;width:100%;font-size:.8rem}} th,td{{padding:.4rem .5rem;text-align:right;white-space:nowrap;border-top:1px solid var(--border)}}
th{{background:var(--panel2);color:var(--ink2);font-size:.72rem;font-weight:600}} th.l,td.l{{text-align:left}} .num{{font-variant-numeric:tabular-nums}} .pos{{color:var(--up)}} .neg{{color:var(--down)}}
.wrap{{overflow-x:auto}} .verdict{{border-left:3px solid var(--s2);padding:.6rem .9rem;background:var(--panel);border-radius:0 8px 8px 0;margin:1rem 0}}
.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:.6rem;margin:1rem 0}} .tile{{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:.6rem .8rem}} .tile .v{{font-size:1.2rem;font-weight:600}} .tile .l{{color:var(--ink2);font-size:.74rem}}
.note{{color:var(--muted);font-size:.76rem;line-height:1.6}} code{{background:var(--panel2);padding:0 .3rem;border-radius:4px}}
</style></head><body><main>
<p><a href="../">← Revenue vs Valuation dashboard</a></p>
<h1>Revenue Breakout Backtest</h1>
<p class="sub">Buy tokens when 7-day protocol revenue breaks out; sell when revenue momentum slows. {R["start"]} → {R["end"]}, {R["n_universe"]} tokens (avg {R["avg_eligible"]:.0f} eligible per day), {R["cost"]*100:.1f}% cost per side, max {R["max_pos"]} positions.</p>
<div id="verdict"></div>
<h2>Equity curves (log scale, start = 1×)</h2>
<div class="card">{curve_svg(R["curves"], [k for k,_,_ in SHOW])}</div>
<h2>Strategy grid vs benchmarks</h2>
<div class="card wrap">{stats_table()}</div>
<p class="note"><b>Exp-matched EW</b> = the equal-weight universe return scaled day-by-day by the strategy's own invested fraction — i.e. what "being in the market that much, in random names" would have returned. <b>Alpha vs matched</b> = strategy total minus that. This separates <i>stock-picking</i> from <i>cash drag / market timing</i>.</p>
<h2>Event study — what happens to price after a revenue breakout</h2>
<div class="card wrap">{events_table()}</div>
<p class="note">Every first-day breakout signal in the universe (not limited by position slots), bought at the next close. <b>Excess</b> = token forward return minus the equal-weight universe over the same window. t-stat on the excess mean; |t| &gt; 2 ≈ statistically meaningful.</p>
{('''<h2>Other revenue strategies — cross-sectional portfolios</h2>
<p class="note">Weekly-rebalanced, equal-weight, long the top quintile of eligible names by each score (≈96% invested, ''' + f"{R['cost']*100:.1f}" + '''% cost on turnover). Because these are always fully invested, compare them to the equal-weight universe, not to cash: <b>Alpha vs EW</b> is the total-return gap. The <b>L/S spread</b> (top minus bottom revenue-momentum quintile) is the pure factor test — it needs no market direction to work, but shorting alts is impractical for most; read it as "how strongly revenue ranks winners from losers."</p>
<div class="card">''' + factor_curve_svg() + '''</div>
<div class="card wrap" style="margin-top:.6rem">''' + factor_table() + '''</div>
<h2>Signal event studies — sell triggers and dip-buys</h2>
<div class="card wrap">''' + factor_events_table() + '''</div>
<p class="note">Same construction as above: every first-day signal, bought/sold at the next close, excess = token forward return minus the equal-weight universe. A significantly <i>negative</i> excess for FADE means it works as a sell/avoid trigger.</p>''') if R2 else ''}
{open("search_section.html").read() if __import__("os").path.exists("search_section.html") else ""}
<h2>Recent trades — Revenue breakout (1.5×, 4-wk high) → exit when rev slows</h2>
<div class="card wrap">{trades_table()}</div>
<h2>Method &amp; caveats</h2>
<p class="note">
<b>Signal.</b> rev7d = trailing 7-day sum of DeFiLlama daily revenue (children summed into the parent protocol). Breakout when rev7d ≥ K × mean(rev7d over the prior 8 weeks, current week excluded) <i>and</i> rev7d is an N-day high. <b>Exit "slows"</b>: rev7d drops below its trailing 4-week average. Variants: two consecutive down weeks; fixed 28-day hold; 25% trailing stop. <b>Price control</b>: identical rules applied to price instead of revenue, to test whether revenue adds information beyond plain momentum.<br>
<b>Execution.</b> Signal on day t (UTC-complete data), trade at close t+1, equal notional per slot, {R["cost"]*100:.1f}% per side. Point-in-time eligibility: ≥$100k revenue in the trailing 30d and ≥90 days of history.<br>
<b>Caveats.</b> Universe = protocols that have a token <i>today</i> and material revenue history — a survivorship bias (dead/delisted tokens are missing), which flatters buy-and-hold benchmarks and the strategy alike. Only ~2 years of clean data. Daily prices from DeFiLlama's price API (CoinGecko-sourced); price prints that jump &gt;300% or fall &gt;90% in a day are treated as feed errors — reverting spikes are masked and non-reverting ones remove the token (this conservatively dropped SPELL, LON, BOO, KTC, FRIEND as bad data and also RAM, SWAP, THE, LVL, which had genuine one-day pumps the strategy might otherwise have caught). Revenue adapters can be revised retroactively. Not investment advice.
</p>
<p class="note">Code: <code>revenue/backtest/bt_engine.py</code> (reproducible; fetches from public APIs).</p>
</main>
<script>
const S = {json.dumps({k: R["stats"][k] for k in R["stats"]})};
const a = S["K1.5_N28_slow"], b = S["K2.0_N56_slow"], p = S["PRICE breakout control"], ew = S["EW universe"], btc = S["BTC"];
const pct = v => v==null ? "—" : (v*100).toFixed(1)+"%";
const best = Object.entries(S).filter(([k])=>k.startsWith("K")).sort((x,y)=>(y[1].alpha_vs_matched||0)-(x[1].alpha_vs_matched||0))[0];
document.getElementById("verdict").innerHTML = `<div class="tiles">
<div class="tile"><div class="v">${{pct(a.total)}}</div><div class="l">rev breakout 1.5×/4wk · total</div></div>
<div class="tile"><div class="v">${{pct(a.alpha_vs_matched)}}</div><div class="l">alpha vs exposure-matched market</div></div>
<div class="tile"><div class="v">${{pct(ew.total)}}</div><div class="l">equal-weight universe · total</div></div>
<div class="tile"><div class="v">${{pct(btc.total)}}</div><div class="l">BTC · total</div></div>
<div class="tile"><div class="v">${{(a.hit*100).toFixed(0)}}% · ${{a.n_trades}}</div><div class="l">hit rate · trades</div></div>
</div>
<div class="verdict">Best variant by alpha-vs-matched: <b>${{best[0]}}</b> (${{pct(best[1].alpha_vs_matched)}} alpha, ${{pct(best[1].total)}} total, exposure ${{pct(best[1].exposure)}}). Price-only control: ${{pct(p.total)}} total, ${{pct(p.alpha_vs_matched)}} alpha.</div>`;
</script>
</body></html>"""
open(OUT, "w").write(html)
print("wrote", OUT, len(html), "bytes")
