# Passive income experiments

Several small, free experiments running side by side. Keep what earns, drop what doesn't.

| # | Experiment | Status | Your one-off steps | Guide |
|---|---|---|---|---|
| 1 | **MoneyMath**: 18 free finance calculators | Built | Turn on GitHub Pages; add tip/ads/analytics codes | [SETUP.md](SETUP.md), [PROMOTION.md](PROMOTION.md) |
| 2 | **Daily Target**: shareable daily numbers puzzle (on the same site at `/daily/`) | Built | None beyond #1; share it | [PROMOTION.md](PROMOTION.md) |
| 3 | **KDP book**: Great British Large Print Word Search | Print-ready | KDP account, upload 2 PDFs | [books/LISTING.md](books/LISTING.md) |
| 4 | **Digital products**: UK budget spreadsheet + printable planner | Ready | Payhip/Gumroad account, upload | [products/LISTING.md](products/LISTING.md) |
| 5 | **Stock photos**: your Jersey photos | Tool ready, waiting for photos | Share photos; Adobe Stock/Alamy accounts | `tools/photos.py` |

## Your checklist (about 1 hour in total, once)

- [ ] GitHub → Settings → Pages → Source: **GitHub Actions** (site goes live at https://uknsaunders.github.io/Idea1/)
- [ ] Free **Cloudflare Web Analytics** or **GoatCounter** → paste the code into `site/assets/config.js`, so you can see what's working
- [ ] **Ko-fi** tip link → `config.js`
- [ ] **Google Search Console**: add the site and submit `sitemap.xml`
- [ ] **KDP**: upload `books/out/wordsearch-interior.pdf` + `wordsearch-cover.pdf`
- [ ] **Payhip**: upload the spreadsheet and planner; add the links to `config.js` → `affiliates`
- [ ] Post the ready-made promotion messages from `PROMOTION.md`
- [ ] Share your photos (never commit them to this public repo)

## Measuring what works (check monthly)

| Experiment | Where to look | Signal that it's worth doubling down |
|---|---|---|
| Calculators | Cloudflare/GoatCounter visits; Search Console impressions | Search impressions growing month on month |
| Daily Target | Visits to `/daily/`; returning visitors | People coming back daily or sharing results |
| KDP book | KDP Reports | Any organic sales in month 1–2, then make Vol. 2 / a Christmas edition |
| Digital products | Payhip dashboard | Sales, or clicks from the calculators (GoatCounter events) |
| Stock photos | Adobe Stock / Alamy dashboards | Downloads within 3 months, then upload more |

## Repo layout

- `build.py` → generates `site/` (calculators, game, sitemap). Run `python3 build.py`.
- `books/` → KDP book generator and themes
- `products/` → spreadsheet and planner generators (outputs are git-ignored because the repo is public)
- `tools/photos.py` → stock-photo screening (strips GPS, flags blur, size and duplicates)
