# Revenue-breakout backtest

Reproduce:

```
python3 bt_universe.py      # protocols with a token + material revenue  -> bt_universe.json
python3 bt_fetch_rev.py     # daily revenue per child protocol (DeFiLlama) -> bt_rev/
python3 bt_fetch_px.py      # daily prices (DeFiLlama price API)         -> bt_px/
python3 bt_engine.py        # breakout signals, portfolio, benchmarks, event study -> bt_results.json
python3 bt_factors.py       # cross-sectional factor portfolios + fade/divergence studies -> bt_results2.json
python3 bt_page.py index.html
```

Needs `pandas` + `numpy`. Everything else is stdlib; all data comes from public APIs, no keys.
Results and methodology: `index.html` (live at `/revenue/backtest/`).
