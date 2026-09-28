# Setup — about 15 minutes, once

Everything is already built. These are the only steps that legally need **you**, because they involve accounts in your name and getting paid.

## 1. Turn the site on (1 minute)

1. Go to **github.com/uknsaunders/Idea1 → Settings → Pages**.
2. Under **Build and deployment → Source**, choose **GitHub Actions**.
3. Go to the **Actions** tab and re-run the latest "Deploy site to GitHub Pages" run (or push any change).

Your site will be live at **https://uknsaunders.github.io/Idea1/**

## 2. Get found on Google (5 minutes, free)

1. Go to <https://search.google.com/search-console> and add the URL-prefix property `https://uknsaunders.github.io/Idea1/`.
2. Choose the **HTML tag** verification method. Copy the `content="..."` value and send it to Claude (or add a `<meta name="google-site-verification" ...>` line in `build.py`'s `layout()` head).
3. Once verified, submit `sitemap.xml` under **Sitemaps**.
4. Do the same at <https://www.bing.com/webmasters> (it can import from Google Search Console in one click).

## 3. Start earning — pick any or all

Edit **`site/assets/config.js`** (you can do it in the GitHub website: open the file → pencil icon → commit). The site redeploys automatically.

| Income source | Sign up | Put in `config.js` |
|---|---|---|
| **Tips** (works from day one) | <https://ko-fi.com> or <https://buymeacoffee.com> — free | `tipUrl: "https://ko-fi.com/yourname"` |
| **Ads** (best once you have traffic) | <https://adsense.google.com> — free. Needs a live site with some content; approval can take days–weeks | `adsenseClient: "ca-pub-XXXXXXXXXXXXXXXX"` |
| **Affiliate links** (highest per-click value in finance) | Savings / investing / credit-comparison affiliate programmes via networks such as Awin, Impact or CJ — free to join | add entries to `affiliates: [...]` |

**AdSense note:** AdSense requires ads on a domain you control and asks for an `ads.txt` file at the domain root. GitHub Pages project sites (`username.github.io/Idea1`) can't serve a root `ads.txt`, so for AdSense you'll likely want either a cheap custom domain (~£10/yr — the only optional cost) or to rename this repo to `uknsaunders.github.io`. Tips and affiliates work fine without either.

## 4. Changing or adding calculators

All pages are generated from `build.py`. Edit it and run `python3 build.py` — or just ask Claude to add a calculator.
