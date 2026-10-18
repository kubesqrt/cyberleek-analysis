# Website Sales Estimator

Estimates an online store's monthly sales from public signals and assumptions:

    net revenue = visits × conversion rate × average order value × (1 − returns)

`index.html` is a self-contained calculator with low / base / high scenarios, a
visits × conversion sensitivity grid, four cross-check calculators, and the
benchmark tables used to pick inputs. Presets live in the `SITES` object at the
bottom of the page; one JSON record per analysed site is kept in `sites/`.

## Procedure per site

1. **Platform and age** — on Shopify read `/products.json` and
   `/collections.json` (earliest `created_at`), policy "last updated" dates,
   shop ID in the page source; WHOIS for an upper bound.
2. **Catalog** — product count, variants, price range and median, vendor
   (print-on-demand vendors mean no inventory and thin margins).
3. **Proof of demand** — reviews app and count, sold-out variants, press.
4. **Marketing footprint** — Meta / TikTok / GA / Pinterest / Snap pixels,
   Meta Ad Library, Klaviyo, social links and follower counts.
5. **Third-party traffic** — Similarweb / Semrush (only report above ~5k
   visits a month; "no data" is itself a signal).
6. Place the store in a traffic tier, pick a conversion band, derive AOV from
   the catalog, net down for returns, and cross-check against reviews, order
   numbers, ad spend or social reach where available.

## Sites analysed

| Site | Checked | Tier | Base net / month | Range |
|---|---|---|---|---|
| veryseason.com | 2026-10-18 | 0 (pre-traction) | ~£15 | £1 – £550 |
