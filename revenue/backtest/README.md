# Revenue-breakout backtest

Reproduce:

```
python3 bt_universe.py      # protocols with a token + material revenue  -> bt_universe.json
python3 bt_fetch_rev.py     # daily revenue per child protocol (DeFiLlama) -> bt_rev/
python3 bt_fetch_px.py      # daily prices (DeFiLlama price API)         -> bt_px/
python3 bt_engine.py        # breakout signals, portfolio, benchmarks, event study -> bt_results.json
python3 bt_factors.py       # cross-sectional factor portfolios + fade/divergence studies -> bt_results2.json
python3 bt_fetch_hrev.py     # holders revenue history (revenue paid to token)
python3 bt_fetch_vol.py      # token volume/mcap history (CoinGecko, last 365d)
python3 bt_capture.py        # holders-revenue variants -> bt_results_capture.json
python3 bt_longhold.py       # long-term revenue-trend holds -> bt_results_longhold.json
python3 bt_search.py         # 108-strategy search + holdout + leverage -> bt_results_search.json
python3 bt_sizing.py         # sizing study + vol-target leverage -> bt_results_sizing.json
python3 bt_combo.py          # joint test of the survivors -> bt_results_combo.json
python3 bt_page2.py && python3 bt_page.py index.html
```

Needs `pandas` + `numpy`. Everything else is stdlib; all data comes from public APIs, no keys.
Results and methodology: `index.html` (live at `/revenue/backtest/`).
