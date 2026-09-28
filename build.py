#!/usr/bin/env python3
"""Generates the static site in ./site from the page definitions below.

Run:  python3 build.py
No dependencies beyond the Python standard library.
"""
import datetime
import html
import json
import os
import pathlib

# Change this if you move the site to a custom domain.
SITE_URL = os.environ.get("SITE_URL", "https://uknsaunders.github.io/Idea1").rstrip("/")
SITE_NAME = "MoneyMath"
OUT = pathlib.Path(__file__).parent / "site"

PAGES = []


def page(slug, title, h1, description, card, script, content, faqs, blurb):
    PAGES.append(dict(slug=slug, title=title, h1=h1, description=description, card=card,
                      script=script, content=content, faqs=faqs, blurb=blurb))


def field(id_, label, value, step="any", suffix=""):
    return (f'<div><label for="{id_}">{label}{suffix}</label>'
            f'<input id="{id_}" type="number" inputmode="decimal" step="{step}" value="{value}"></div>')


def stat(id_, label):
    return f'<div class="stat"><div class="k">{label}</div><div class="v" id="{id_}">—</div></div>'


# ── Compound interest ────────────────────────────────────────
page(
    "compound-interest-calculator",
    "Compound Interest Calculator — with Monthly Contributions",
    "Compound Interest Calculator",
    "Free compound interest calculator with monthly contributions. See how your savings or investments grow year by year, with a chart and full breakdown.",
    '<div class="grid">'
    + field("p", "Starting amount", 10000)
    + field("m", "Monthly contribution", 250)
    + field("r", "Annual interest rate (%)", 7)
    + field("y", "Years", 20, step="1")
    + '<div><label for="c">Compounding</label><select class="field" id="c">'
      '<option value="12" selected>Monthly</option><option value="4">Quarterly</option>'
      '<option value="1">Yearly</option><option value="365">Daily</option></select></div>'
    + "</div>"
    '<div class="results">' + stat("fv", "Final balance") + stat("tc", "Total contributed") + stat("ti", "Total interest earned") + "</div>"
    '<div class="chart" id="chart"></div>'
    '<div class="table-wrap"><table><thead><tr><th>Year</th><th>Contributed</th><th>Interest</th><th>Balance</th></tr></thead><tbody id="rows"></tbody></table></div>',
    """
App.bind(() => {
  const P = App.val("p"), M = App.val("m"), r = App.val("r") / 100, Y = Math.round(App.val("y"));
  const n = parseFloat(document.getElementById("c").value);
  const monthly = Math.pow(1 + r / n, n / 12) - 1;   // effective monthly rate
  let bal = P, contrib = P; const labels = [], cs = [], is = []; let rows = "";
  for (let yr = 1; yr <= Y; yr++) {
    for (let mo = 0; mo < 12; mo++) { bal = bal * (1 + monthly) + M; contrib += M; }
    labels.push(yr); cs.push(contrib); is.push(bal - contrib);
    rows += `<tr><td>${yr}</td><td>${App.money(contrib)}</td><td>${App.money(bal - contrib)}</td><td>${App.money(bal)}</td></tr>`;
  }
  App.set("fv", App.money(bal)); App.set("tc", App.money(contrib)); App.set("ti", App.money(bal - contrib));
  document.getElementById("rows").innerHTML = rows;
  App.chart(document.getElementById("chart"), labels, [
    { label: "Contributions", color: "var(--accent-2)", values: cs },
    { label: "Interest", color: "var(--accent)", values: is },
  ]);
});
""",
    """
<h2>How compound interest works</h2>
<p>Compound interest means you earn interest on your interest. Each period, the interest you earned is added to your balance, so the next period's interest is calculated on a bigger number. Over long periods this snowball effect becomes the main driver of growth — often more than the money you put in yourself.</p>
<h2>The formula</h2>
<p>For a lump sum: <code>A = P × (1 + r/n)<sup>n×t</sup></code>, where <em>P</em> is the starting amount, <em>r</em> the annual rate, <em>n</em> the number of compounding periods per year and <em>t</em> the number of years. This calculator also adds your monthly contributions and compounds them at the same effective rate.</p>
<h2>Tips for making compounding work for you</h2>
<ul>
<li><strong>Start early.</strong> Time is the most powerful variable — try changing the years above and watch the interest bar grow.</li>
<li><strong>Contribute regularly.</strong> Small, automatic monthly contributions add up dramatically.</li>
<li><strong>Keep fees low.</strong> A 1% annual fee reduces your effective rate by 1% every single year.</li>
</ul>
""",
    [
        ("What is a realistic interest rate to use?", "Savings accounts typically pay 1–5%. Long-term stock market returns have historically averaged around 7% a year after inflation, but returns are never guaranteed."),
        ("Does compounding frequency matter much?", "A little. Daily compounding beats yearly compounding, but the difference is small compared with the effect of the rate and the number of years."),
        ("Is this calculator free?", "Yes — completely free, with no sign-up. Everything is calculated in your browser and nothing is stored or sent anywhere."),
    ],
    "See how savings and investments grow with regular contributions.",
)

# ── Loan / mortgage ──────────────────────────────────────────
page(
    "mortgage-calculator",
    "Mortgage & Loan Repayment Calculator — Monthly Payments",
    "Mortgage & Loan Repayment Calculator",
    "Free mortgage and loan calculator. Work out your monthly repayment, total interest and see how overpayments shorten your loan, with an amortisation schedule.",
    '<div class="grid">'
    + field("a", "Loan amount", 250000)
    + field("r", "Interest rate (%)", 4.5)
    + field("y", "Term (years)", 25, step="1")
    + field("x", "Extra monthly overpayment", 0)
    + "</div>"
    '<div class="results">' + stat("pm", "Monthly payment") + stat("ti", "Total interest") + stat("tp", "Total repaid") + stat("tm", "Paid off in") + "</div>"
    '<p class="note" id="saved"></p>'
    '<div class="chart" id="chart"></div>'
    '<div class="table-wrap"><table><thead><tr><th>Year</th><th>Principal paid</th><th>Interest paid</th><th>Balance left</th></tr></thead><tbody id="rows"></tbody></table></div>',
    """
function run(A, i, N, X) {
  const pay = i === 0 ? A / N : A * i / (1 - Math.pow(1 + i, -N));
  let bal = A, months = 0, interest = 0, yp = 0, yi = 0; const yearly = [];
  while (bal > 0.005 && months < 1200) {
    const int = bal * i, princ = Math.min(bal, pay + X - int);
    bal -= princ; interest += int; yp += princ; yi += int; months++;
    if (months % 12 === 0 || bal <= 0.005) { yearly.push([yp, yi, Math.max(bal, 0)]); yp = yi = 0; }
  }
  return { pay, months, interest, yearly };
}
App.bind(() => {
  const A = App.val("a"), i = App.val("r") / 100 / 12, N = Math.round(App.val("y") * 12), X = App.val("x");
  if (N <= 0) return;
  const r = run(A, i, N, X), base = run(A, i, N, 0);
  App.set("pm", App.money(r.pay + X, 2));
  App.set("ti", App.money(r.interest));
  App.set("tp", App.money(A + r.interest));
  App.set("tm", `${Math.floor(r.months / 12)} yrs ${r.months % 12} mo`);
  App.set("saved", X > 0 ? `Overpaying saves you ${App.money(base.interest - r.interest)} in interest and ${Math.floor((base.months - r.months) / 12)} yrs ${(base.months - r.months) % 12} mo.` : "Tip: try an overpayment to see how much interest you could save.");
  document.getElementById("rows").innerHTML = r.yearly.map((y, k) => `<tr><td>${k + 1}</td><td>${App.money(y[0])}</td><td>${App.money(y[1])}</td><td>${App.money(y[2])}</td></tr>`).join("");
  App.chart(document.getElementById("chart"), r.yearly.map((_, k) => k + 1), [
    { label: "Principal", color: "var(--accent-2)", values: r.yearly.map((y) => y[0]) },
    { label: "Interest", color: "var(--accent)", values: r.yearly.map((y) => y[1]) },
  ]);
});
""",
    """
<h2>How repayments are calculated</h2>
<p>A standard repayment (amortising) loan has a fixed monthly payment: <code>M = P × i / (1 − (1 + i)<sup>−n</sup>)</code>, where <em>P</em> is the loan amount, <em>i</em> the monthly interest rate and <em>n</em> the number of monthly payments. Early on, most of each payment is interest; later, most of it pays down the balance — the chart above shows this shift.</p>
<h2>Why overpaying is so powerful</h2>
<p>Every extra payment goes straight to the balance, so you stop paying interest on that money for the rest of the term. Even a small monthly overpayment can take years off a mortgage. Check whether your lender charges early repayment fees before overpaying.</p>
""",
    [
        ("Does this work for car loans and personal loans?", "Yes. Any fixed-rate loan with equal monthly payments works the same way — just enter the amount, rate and term."),
        ("Does this include taxes, insurance or fees?", "No. It calculates principal and interest only. Add property taxes, insurance and any lender fees on top."),
        ("What is an amortisation schedule?", "It's the breakdown of each payment into interest and principal over the life of the loan. The table above shows it by year."),
    ],
    "Monthly payments, total interest and the effect of overpaying.",
)

# ── Savings goal ─────────────────────────────────────────────
page(
    "savings-goal-calculator",
    "Savings Goal Calculator — How Much to Save Each Month",
    "Savings Goal Calculator",
    "Free savings goal calculator. Find out how much you need to save each month to reach your target by a set date, including interest.",
    '<div class="grid">'
    + field("g", "Savings goal", 20000)
    + field("s", "Already saved", 2000)
    + field("r", "Interest rate (%)", 4)
    + field("y", "Years to reach goal", 3, step="0.5")
    + "</div>"
    '<div class="results">' + stat("pm", "Save each month") + stat("pw", "…or each week") + stat("ti", "Interest earned") + "</div>",
    """
App.bind(() => {
  const G = App.val("g"), S = App.val("s"), i = App.val("r") / 100 / 12, N = Math.max(1, Math.round(App.val("y") * 12));
  const grow = Math.pow(1 + i, N);
  const need = G - S * grow;
  const pm = need <= 0 ? 0 : (i === 0 ? need / N : need * i / (grow - 1));
  App.set("pm", App.money(pm, 2));
  App.set("pw", App.money(pm * 12 / 52, 2));
  App.set("ti", App.money(Math.max(0, G - S - pm * N)));
});
""",
    """
<h2>How it works</h2>
<p>The calculator works backwards from your goal. It grows what you've already saved at your interest rate, then works out the fixed monthly deposit that closes the gap by your deadline, using the future-value-of-an-annuity formula.</p>
<h2>Ideas for common goals</h2>
<ul><li>Emergency fund: 3–6 months of essential spending.</li><li>House deposit: typically 5–20% of the property price.</li><li>Holiday, wedding or car: pick the date, then automate the monthly amount on payday.</li></ul>
""",
    [
        ("Where should I keep short-term savings?", "For goals under ~5 years, most people use easy-access or fixed-term savings accounts rather than investments, because the value won't fall."),
        ("What if I already have enough?", "If your current savings plus interest reach the goal on their own, the monthly amount shows as zero."),
    ],
    "How much to save each month to hit a target by a deadline.",
)

# ── FIRE / retirement ────────────────────────────────────────
page(
    "fire-calculator",
    "FIRE Calculator — When Can I Retire Early?",
    "FIRE Calculator: When Can You Retire?",
    "Free FIRE (Financial Independence, Retire Early) calculator. Find your FI number and how many years until your investments can cover your spending.",
    '<div class="grid">'
    + field("sp", "Annual spending in retirement", 30000)
    + field("inv", "Currently invested", 50000)
    + field("sv", "Amount invested per year", 15000)
    + field("r", "Expected real return (%)", 5)
    + field("w", "Safe withdrawal rate (%)", 4)
    + "</div>"
    '<div class="results">' + stat("fi", "Your FI number") + stat("yrs", "Years to financial independence") + stat("pct", "Progress so far") + "</div>"
    '<div class="chart" id="chart"></div>',
    """
App.bind(() => {
  const sp = App.val("sp"), inv = App.val("inv"), sv = App.val("sv"), r = App.val("r") / 100, w = App.val("w") / 100;
  if (w <= 0) return;
  const target = sp / w;
  let bal = inv, yr = 0; const labels = [], vals = [];
  while (bal < target && yr < 100) { bal = bal * (1 + r) + sv; yr++; labels.push(yr); vals.push(bal); }
  App.set("fi", App.money(target));
  App.set("yrs", bal >= target ? (yr === 0 ? "You're there!" : `${yr} years`) : "100+ years");
  App.set("pct", `${App.num(Math.min(100, inv / target * 100), 1)}%`);
  App.chart(document.getElementById("chart"), labels, [
    { label: "Portfolio", color: "var(--accent)", values: vals.map((v) => Math.min(v, target)) },
    { label: "Remaining to FI", color: "var(--accent-2)", values: vals.map((v) => Math.max(0, target - v)) },
  ]);
});
""",
    """
<h2>What is FIRE?</h2>
<p>FIRE stands for Financial Independence, Retire Early. The idea is to save and invest aggressively until your investments are large enough that withdrawals can cover your living costs indefinitely — at which point work becomes optional.</p>
<h2>Your FI number and the 4% rule</h2>
<p>Your FI number is your annual spending divided by your safe withdrawal rate. At 4%, that's 25× your annual spending. The 4% rule comes from historical research suggesting a portfolio could sustain that withdrawal rate (adjusted for inflation) for around 30 years. Many early retirees use 3–3.5% for extra safety over longer retirements.</p>
<h2>The biggest lever: your savings rate</h2>
<p>Cutting spending helps twice: you save more each year <em>and</em> your FI number gets smaller. Try lowering the spending figure above to see the effect.</p>
""",
    [
        ("Why use a 'real' return?", "A real return is after inflation. Using it keeps every number in today's money, so your FI number stays meaningful."),
        ("Is the 4% rule guaranteed?", "No. It's based on historical returns and future markets may differ. Treat this as a planning estimate, not financial advice."),
    ],
    "Your FI number and how many years until you can retire.",
)

# ── Inflation ────────────────────────────────────────────────
page(
    "inflation-calculator",
    "Inflation Calculator — Future Value & Purchasing Power",
    "Inflation Calculator",
    "Free inflation calculator. See what money today will be worth in the future, and how much you'll need to keep the same purchasing power.",
    '<div class="grid">'
    + field("a", "Amount today", 1000)
    + field("r", "Average inflation rate (%)", 3)
    + field("y", "Years", 10, step="1")
    + "</div>"
    '<div class="results">' + stat("need", "Cost of the same things in future") + stat("worth", "What today's money will buy") + stat("loss", "Purchasing power lost") + "</div>",
    """
App.bind(() => {
  const a = App.val("a"), r = App.val("r") / 100, y = App.val("y");
  const f = Math.pow(1 + r, y);
  App.set("need", App.money(a * f));
  App.set("worth", App.money(a / f));
  App.set("loss", `${App.num((1 - 1 / f) * 100, 1)}%`);
});
""",
    """
<h2>How inflation erodes your money</h2>
<p>Inflation is the general rise in prices over time. If prices rise 3% a year, something costing 1,000 today costs about 1,344 in ten years — and 1,000 kept in cash will only buy about 744 worth of today's goods. That's why cash savings earning less than inflation lose real value.</p>
<h2>The formula</h2>
<p>Future cost = amount × (1 + inflation)<sup>years</sup>. Purchasing power = amount ÷ (1 + inflation)<sup>years</sup>.</p>
""",
    [
        ("What inflation rate should I use?", "Many central banks target around 2%. The long-run average in most developed economies has been roughly 2–4%."),
        ("How do I beat inflation?", "Your savings or investments need to earn a return higher than the inflation rate. Compare rates using our compound interest calculator."),
    ],
    "What your money will be worth in the future.",
)

# ── Percentage ───────────────────────────────────────────────
page(
    "percentage-calculator",
    "Percentage Calculator — Percent of, Change & Increase",
    "Percentage Calculator",
    "Free percentage calculator. Work out X% of a number, what percent one number is of another, and percentage increase or decrease.",
    '<h2 style="margin-top:0">What is X% of Y?</h2><div class="grid">' + field("a1", "Percent (%)", 15) + field("b1", "Of number", 200) + "</div>"
    '<div class="results">' + stat("o1", "Result") + "</div>"
    '<h2>X is what percent of Y?</h2><div class="grid">' + field("a2", "Number", 30) + field("b2", "Of total", 120) + "</div>"
    '<div class="results">' + stat("o2", "Percentage") + "</div>"
    '<h2>Percentage change from X to Y</h2><div class="grid">' + field("a3", "From", 80) + field("b3", "To", 100) + "</div>"
    '<div class="results">' + stat("o3", "Change") + "</div>",
    """
App.bind(() => {
  App.set("o1", App.num(App.val("a1") / 100 * App.val("b1"), 4));
  const b2 = App.val("b2"); App.set("o2", b2 ? `${App.num(App.val("a2") / b2 * 100, 4)}%` : "—");
  const a3 = App.val("a3"), ch = a3 ? (App.val("b3") - a3) / Math.abs(a3) * 100 : NaN;
  App.set("o3", isFinite(ch) ? `${ch >= 0 ? "+" : ""}${App.num(ch, 4)}%` : "—");
});
""",
    """
<h2>Percentage formulas</h2>
<ul>
<li><strong>X% of Y</strong> = X ÷ 100 × Y</li>
<li><strong>X as a percent of Y</strong> = X ÷ Y × 100</li>
<li><strong>Percentage change</strong> = (new − old) ÷ old × 100</li>
</ul>
<p>Common uses: discounts and sale prices, tips, VAT and sales tax, pay rises, investment returns and exam scores.</p>
""",
    [
        ("How do I add a percentage to a number?", "Multiply by (1 + percent/100). For example, 200 plus 15% is 200 × 1.15 = 230."),
        ("Why isn't a 50% drop undone by a 50% rise?", "Because the rise is calculated on the smaller number. 100 falls 50% to 50, and 50 rising 50% is only 75."),
    ],
    "Percent of, what percent, and percentage change.",
)


# ── Rendering ────────────────────────────────────────────────
def layout(title, description, path, body, extra_head=""):
    canonical = f"{SITE_URL}/{path}"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} | {SITE_NAME}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>💷</text></svg>">
<link rel="stylesheet" href="{'../' if path else ''}assets/style.css">
{extra_head}
</head>
<body>
<header class="site"><div class="wrap">
<a class="brand" href="{'../' if path else './'}">Money<span>Math</span></a>
<label style="margin:0;font-weight:400">Currency <select id="currency" aria-label="Currency"></select></label>
</div></header>
<main class="wrap">
{body}
</main>
<footer class="site"><div class="wrap">
<p>{" · ".join(f'<a href="{"../" if path else ""}{p["slug"]}/">{p["h1"].split(":")[0]}</a>' for p in PAGES)}</p>
<p>Calculations run entirely in your browser — nothing is stored or sent. Results are estimates for educational purposes, not financial advice. <a href="{'../' if path else ''}privacy.html">Privacy</a></p>
</div></footer>
<script src="{'../' if path else ''}assets/config.js"></script>
<script src="{'../' if path else ''}assets/app.js"></script>
</body>
</html>
"""


def build():
    OUT.mkdir(exist_ok=True)
    today = datetime.date.today().isoformat()

    for p in PAGES:
        faq_ld = {
            "@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faqs"]],
        }
        app_ld = {
            "@context": "https://schema.org", "@type": "WebApplication", "name": p["h1"],
            "url": f"{SITE_URL}/{p['slug']}/", "applicationCategory": "FinanceApplication",
            "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0"},
        }
        head = "".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in (app_ld, faq_ld))
        others = "".join(f'<a href="../{o["slug"]}/"><strong>{o["h1"].split(":")[0]}</strong><span>{o["blurb"]}</span></a>'
                         for o in PAGES if o is not p)
        faqs = "".join(f"<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>" for q, a in p["faqs"])
        body = f"""<h1>{p['h1']}</h1>
<p class="lede">{html.escape(p['description'])}</p>
<section class="card">{p['card']}</section>
<div class="ad-slot"></div>
<section class="card promo" id="promo" hidden></section>
<article>{p['content']}</article>
<h2>Frequently asked questions</h2>
{faqs}
<div class="ad-slot"></div>
<h2>More free calculators</h2>
<div class="tools">{others}</div>
<script>document.addEventListener("DOMContentLoaded", () => {{{p['script']}}});</script>"""
        d = OUT / p["slug"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(layout(p["title"], p["description"], f"{p['slug']}/", body, head))

    tools = "".join(f'<a href="{p["slug"]}/"><strong>{p["h1"].split(":")[0]}</strong><span>{p["blurb"]}</span></a>' for p in PAGES)
    home = f"""<h1>Free money calculators</h1>
<p class="lede">Fast, private, no-sign-up calculators for savings, loans, mortgages, retirement and more. Everything runs in your browser.</p>
<div class="tools">{tools}</div>
<div class="ad-slot"></div>
<section class="card promo" id="promo" hidden></section>
<h2>Why MoneyMath?</h2>
<p>Most financial calculators are buried under pop-ups or ask for your email. These don't. Pick a calculator, change the numbers, and the results update instantly — with charts and year-by-year breakdowns where they help.</p>"""
    (OUT / "index.html").write_text(layout(f"{SITE_NAME} — Free Finance Calculators",
                                           "Free, private finance calculators: compound interest, mortgage, savings goal, FIRE retirement, inflation and percentages. No sign-up.",
                                           "", home))

    privacy = """<h1>Privacy</h1>
<p>All calculations happen in your browser. We don't collect, store or transmit the numbers you enter.</p>
<p>Your currency choice is saved in your browser's local storage so it's remembered next visit.</p>
<p>This site may show adverts from Google AdSense. Google and its partners may use cookies to serve ads based on your visits to this and other websites. You can opt out of personalised advertising at <a href="https://adssettings.google.com">Google Ads Settings</a>. See <a href="https://policies.google.com/technologies/partner-sites">how Google uses data from partner sites</a>.</p>
<p>Some links may be affiliate links, meaning we may earn a commission at no extra cost to you.</p>"""
    (OUT / "privacy.html").write_text(layout("Privacy Policy", "Privacy policy for MoneyMath free calculators.", "", privacy))

    urls = [""] + [f"{p['slug']}/" for p in PAGES] + ["privacy.html"]
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{SITE_URL}/{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls)
        + "</urlset>\n")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    (OUT / ".nojekyll").write_text("")
    print(f"Built {len(PAGES)} calculators + home, privacy, sitemap → {OUT}")


if __name__ == "__main__":
    build()
