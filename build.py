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


# ── UK take-home pay ─────────────────────────────────────────
page(
    "uk-take-home-pay-calculator",
    "UK Take-Home Pay Calculator 2026/27 — Salary After Tax & NI",
    "UK Take-Home Pay Calculator (2026/27)",
    "Free UK salary calculator for 2026/27. See your take-home pay after income tax, National Insurance and pension, per year, month and week.",
    '<div class="grid">'
    + field("g", "Annual salary (£)", 35000)
    + field("p", "Pension contribution (% of salary)", 5)
    + "</div>"
    '<div class="results">' + stat("ny", "Take-home per year") + stat("nm", "Per month") + stat("nw", "Per week")
    + stat("tx", "Income tax") + stat("ni", "National Insurance") + stat("pn", "Pension") + "</div>"
    '<p class="note">England, Wales &amp; Northern Ireland rates. Pension treated as salary sacrifice. Excludes student loans and Scottish rates.</p>',
    """
App.bind(() => {
  const G = App.val("g"), pen = G * App.val("p") / 100, adj = Math.max(0, G - pen);
  const PA = Math.max(0, 12570 - Math.max(0, adj - 100000) / 2);
  const T = Math.max(0, adj - PA);
  const tax = Math.min(T, 37700) * 0.2 + Math.max(0, Math.min(T, 125140) - 37700) * 0.4 + Math.max(0, T - 125140) * 0.45;
  const ni = Math.max(0, Math.min(adj, 50270) - 12570) * 0.08 + Math.max(0, adj - 50270) * 0.02;
  const net = adj - tax - ni;
  App.set("ny", App.money(net)); App.set("nm", App.money(net / 12, 2)); App.set("nw", App.money(net / 52, 2));
  App.set("tx", App.money(tax)); App.set("ni", App.money(ni)); App.set("pn", App.money(pen));
});
""",
    """
<h2>How UK income tax works in 2026/27</h2>
<ul>
<li><strong>Personal allowance:</strong> the first £12,570 is tax-free. It shrinks by £1 for every £2 earned over £100,000, disappearing entirely at £125,140.</li>
<li><strong>Basic rate (20%):</strong> the next £37,700 of taxable income.</li>
<li><strong>Higher rate (40%):</strong> taxable income from £37,701 to £125,140.</li>
<li><strong>Additional rate (45%):</strong> above £125,140.</li>
</ul>
<h2>National Insurance</h2>
<p>Employees pay Class 1 NI of 8% on earnings between £12,570 and £50,270, and 2% above that.</p>
<h2>The £100k tax trap</h2>
<p>Between £100,000 and £125,140 you lose personal allowance as you earn more, creating an effective 60% tax rate (62% with NI). Pension contributions via salary sacrifice can bring income back below £100,000 — try it above.</p>
""",
    [
        ("Does this include student loan repayments?", "No. Student loan repayments depend on your plan type and are deducted on top of the figures shown."),
        ("Does it work for Scotland?", "No — Scotland has its own income tax bands. National Insurance is the same across the UK."),
        ("What is salary sacrifice?", "You give up part of your salary in exchange for an employer pension contribution. It reduces both income tax and National Insurance."),
    ],
    "Salary after income tax, NI and pension.",
)

# ── Stamp duty ───────────────────────────────────────────────
page(
    "stamp-duty-calculator",
    "Stamp Duty Calculator (SDLT) — England & Northern Ireland",
    "Stamp Duty Calculator",
    "Free Stamp Duty Land Tax (SDLT) calculator for England and Northern Ireland. Includes first-time buyer relief and the additional property surcharge.",
    '<div class="grid">'
    + field("v", "Property price (£)", 350000)
    + '<div><label for="t">Buyer type</label><select class="field" id="t">'
      '<option value="std">Moving home / standard</option><option value="ftb">First-time buyer</option>'
      '<option value="add">Additional property / buy-to-let</option></select></div>'
    + "</div>"
    '<div class="results">' + stat("sd", "Stamp duty to pay") + stat("er", "Effective rate") + "</div>"
    '<p class="note" id="nt"></p>'
    '<div class="table-wrap"><table><thead><tr><th>Band</th><th>Rate</th><th>Tax</th></tr></thead><tbody id="rows"></tbody></table></div>',
    """
App.bind(() => {
  const V = App.val("v"), t = document.getElementById("t").value;
  let bands = [[125000, 0], [250000, 0.02], [925000, 0.05], [1500000, 0.10], [Infinity, 0.12]], note = "";
  if (t === "ftb") {
    if (V <= 500000) bands = [[300000, 0], [500000, 0.05]];
    else note = "First-time buyer relief isn't available above £500,000, so standard rates apply.";
  }
  const extra = t === "add" ? 0.05 : 0;
  if (t === "add") note = "Includes the 5% surcharge on additional properties. Purchases under £40,000 are exempt.";
  let prev = 0, total = 0, rows = "";
  for (const [top, rate] of bands) {
    if (V <= prev) break;
    const slice = Math.min(V, top) - prev, r = rate + extra, tax = slice * r;
    total += tax;
    rows += `<tr><td>${App.money(prev)} – ${top === Infinity ? "above" : App.money(top)}</td><td>${App.num(r * 100)}%</td><td>${App.money(tax)}</td></tr>`;
    prev = top;
  }
  if (t === "add" && V < 40000) { total = 0; }
  App.set("sd", App.money(total)); App.set("er", V ? `${App.num(total / V * 100, 2)}%` : "—");
  App.set("nt", note); document.getElementById("rows").innerHTML = rows;
});
""",
    """
<h2>Stamp duty rates (from 1 April 2025)</h2>
<table><thead><tr><th>Property price</th><th>Standard rate</th></tr></thead><tbody>
<tr><td>Up to £125,000</td><td>0%</td></tr><tr><td>£125,001 – £250,000</td><td>2%</td></tr>
<tr><td>£250,001 – £925,000</td><td>5%</td></tr><tr><td>£925,001 – £1.5 million</td><td>10%</td></tr>
<tr><td>Above £1.5 million</td><td>12%</td></tr></tbody></table>
<p><strong>First-time buyers</strong> pay 0% up to £300,000 and 5% from £300,001 to £500,000. Above £500,000, standard rates apply to the whole price.</p>
<p><strong>Additional properties</strong> (second homes, buy-to-let) pay an extra 5% on every band.</p>
<p>Scotland (LBTT) and Wales (LTT) have their own systems. Non-UK residents pay a further 2% surcharge, not included here.</p>
""",
    [
        ("When do I pay stamp duty?", "Within 14 days of completion. Your solicitor or conveyancer normally handles it."),
        ("Is stamp duty charged on the whole price?", "No — like income tax, each rate applies only to the portion of the price within that band."),
    ],
    "SDLT for movers, first-time buyers and second homes.",
)

# ── Credit card payoff ───────────────────────────────────────
page(
    "credit-card-payoff-calculator",
    "Credit Card Payoff Calculator — How Long to Clear Your Balance",
    "Credit Card Payoff Calculator",
    "Free credit card payoff calculator. See how many months it takes to clear your balance and how much interest you'll pay at any monthly payment.",
    '<div class="grid">'
    + field("b", "Balance owed", 3000)
    + field("r", "APR (%)", 24.9)
    + field("m", "Monthly payment", 150)
    + "</div>"
    '<div class="results">' + stat("mo", "Time to pay off") + stat("ti", "Total interest") + stat("tp", "Total paid") + "</div>"
    '<p class="note" id="nt"></p>',
    """
App.bind(() => {
  const B = App.val("b"), i = Math.pow(1 + App.val("r") / 100, 1 / 12) - 1, M = App.val("m");
  if (M <= B * i) {
    App.set("mo", "Never"); App.set("ti", "—"); App.set("tp", "—");
    App.set("nt", `Your payment doesn't cover the monthly interest (${App.money(B * i, 2)}). Pay more to reduce the balance.`);
    return;
  }
  let bal = B, n = 0, int = 0;
  while (bal > 0.005 && n < 1200) { const x = bal * i; int += x; bal = bal + x - M; n++; }
  App.set("mo", `${Math.floor(n / 12)} yrs ${n % 12} mo`); App.set("ti", App.money(int)); App.set("tp", App.money(B + int));
  App.set("nt", "Tip: moving the balance to a 0% balance-transfer card could save most of this interest.");
});
""",
    """
<h2>Why minimum payments cost so much</h2>
<p>Credit card APRs are high, so when you only pay a little more than the interest each month, most of your payment never touches the balance. Increasing your payment even slightly can cut years off the debt.</p>
<h2>Ways to pay off faster</h2>
<ul><li>Pay a fixed amount rather than the shrinking minimum.</li><li>Consider a 0% balance transfer card (watch the transfer fee and the end date).</li><li>With several debts, use our debt payoff calculator to compare snowball and avalanche strategies.</li></ul>
""",
    [
        ("How is monthly interest calculated from APR?", "This calculator converts the APR to an equivalent monthly rate. Card issuers' exact methods vary slightly (e.g. daily balances), so treat results as close estimates."),
    ],
    "How long to clear a card balance and the interest cost.",
)

# ── Debt snowball vs avalanche ───────────────────────────────
_debt_rows = "".join(
    f'<div class="grid" style="margin-bottom:10px">{field(f"b{k}", f"Debt {k} balance", b)}{field(f"r{k}", "APR (%)", r)}{field(f"m{k}", "Minimum payment", m)}</div>'
    for k, (b, r, m) in enumerate([(2500, 22.9, 60), (6000, 9.9, 150), (800, 12.9, 25), (0, 0, 0)], 1))
page(
    "debt-payoff-calculator",
    "Debt Payoff Calculator — Snowball vs Avalanche",
    "Debt Payoff Calculator: Snowball vs Avalanche",
    "Free debt payoff calculator comparing the snowball and avalanche methods. Enter up to four debts and an extra monthly payment to see your debt-free date.",
    _debt_rows + '<div class="grid">' + field("x", "Extra payment per month", 100) + "</div>"
    '<div class="results">' + stat("am", "Avalanche: debt-free in") + stat("ai", "Avalanche: interest")
    + stat("sm", "Snowball: debt-free in") + stat("si", "Snowball: interest") + "</div>"
    '<p class="note" id="nt"></p>',
    """
function sim(debts, extra, order) {
  debts = debts.map((d) => ({ ...d })); let n = 0, int = 0;
  while (debts.some((d) => d.b > 0.005) && n < 1200) {
    let pool = extra;
    debts.forEach((d) => { if (d.b > 0) { const x = d.b * d.i; d.b += x; int += x; } });
    debts.forEach((d) => { if (d.b > 0) { const p = Math.min(d.b, d.m); d.b -= p; pool += d.m - p; } else pool += d.m; });
    debts.filter((d) => d.b > 0).sort(order).forEach((d) => { const p = Math.min(d.b, pool); d.b -= p; pool -= p; });
    n++;
  }
  return { n, int };
}
App.bind(() => {
  const debts = [1, 2, 3, 4].map((k) => ({ b: App.val("b" + k), i: App.val("r" + k) / 100 / 12, m: App.val("m" + k) })).filter((d) => d.b > 0);
  const fmt = (n) => n >= 1200 ? "Never" : `${Math.floor(n / 12)} yrs ${n % 12} mo`;
  const a = sim(debts, App.val("x"), (p, q) => q.i - p.i), s = sim(debts, App.val("x"), (p, q) => p.b - q.b);
  App.set("am", fmt(a.n)); App.set("ai", App.money(a.int)); App.set("sm", fmt(s.n)); App.set("si", App.money(s.int));
  App.set("nt", a.n >= 1200 ? "Payments don't cover the interest — increase your extra payment." :
    `Avalanche saves ${App.money(Math.max(0, s.int - a.int))} in interest; snowball clears your first debt sooner, which many people find motivating.`);
});
""",
    """
<h2>Snowball vs avalanche</h2>
<p>Both methods pay the minimum on every debt and put all spare money toward one target debt. When it's cleared, its payment rolls onto the next — so your payments "snowball".</p>
<ul><li><strong>Avalanche:</strong> target the highest interest rate first. Mathematically cheapest.</li>
<li><strong>Snowball:</strong> target the smallest balance first. Quick wins keep you motivated.</li></ul>
<p>The best method is the one you'll stick with. The difference is often smaller than people expect.</p>
""",
    [
        ("Should I save or pay off debt first?", "Most guidance suggests a small emergency fund first, then attacking high-interest debt, since card interest usually exceeds what savings earn."),
    ],
    "Compare snowball and avalanche debt strategies.",
)

# ── Salary converter ─────────────────────────────────────────
page(
    "salary-converter",
    "Salary Converter — Hourly, Daily, Weekly, Monthly & Annual Pay",
    "Salary Converter",
    "Free salary converter. Turn an hourly rate into an annual salary or vice versa, and see daily, weekly and monthly equivalents.",
    '<div class="grid">'
    + field("a", "Amount", 15)
    + '<div><label for="per">Per</label><select class="field" id="per"><option value="h" selected>Hour</option><option value="d">Day</option>'
      '<option value="w">Week</option><option value="m">Month</option><option value="y">Year</option></select></div>'
    + field("h", "Hours per week", 37.5)
    + field("wk", "Weeks worked per year", 52)
    + "</div>"
    '<div class="results">' + stat("oh", "Hourly") + stat("od", "Daily") + stat("ow", "Weekly") + stat("om", "Monthly") + stat("oy", "Annual") + "</div>",
    """
App.bind(() => {
  const a = App.val("a"), h = App.val("h") || 1, wk = App.val("wk") || 1, per = document.getElementById("per").value;
  const yearly = { h: a * h * wk, d: a * 5 * wk, w: a * wk, m: a * 12, y: a }[per];
  App.set("oh", App.money(yearly / wk / h, 2)); App.set("od", App.money(yearly / wk / 5, 2));
  App.set("ow", App.money(yearly / wk, 2)); App.set("om", App.money(yearly / 12, 2)); App.set("oy", App.money(yearly));
});
""",
    """
<h2>How the conversion works</h2>
<p>Annual pay = hourly rate × hours per week × weeks per year. A standard UK full-time week is 37.5 hours. If you're paid for holidays, keep weeks at 52; if you're self-employed and unpaid on holiday, reduce it (e.g. 46–48).</p>
<p>These are gross (before tax) figures. For pay after tax, use the UK take-home pay calculator.</p>
""",
    [("How many working days are in a year?", "About 260 weekdays; roughly 252 after UK bank holidays, and fewer again after annual leave.")],
    "Convert between hourly, daily, monthly and annual pay.",
)

# ── VAT ──────────────────────────────────────────────────────
page(
    "vat-calculator",
    "VAT Calculator — Add or Remove VAT at 20%",
    "VAT Calculator",
    "Free VAT calculator. Add VAT to a net price or remove VAT from a gross price at 20% or any custom rate.",
    '<div class="grid">' + field("a", "Amount", 100) + field("r", "VAT rate (%)", 20) + "</div>"
    '<h2>Adding VAT</h2><div class="results">' + stat("ag", "Price including VAT") + stat("av", "VAT added") + "</div>"
    '<h2>Removing VAT</h2><div class="results">' + stat("rn", "Price excluding VAT") + stat("rv", "VAT included") + "</div>",
    """
App.bind(() => {
  const a = App.val("a"), r = App.val("r") / 100;
  App.set("ag", App.money(a * (1 + r), 2)); App.set("av", App.money(a * r, 2));
  App.set("rn", App.money(a / (1 + r), 2)); App.set("rv", App.money(a - a / (1 + r), 2));
});
""",
    """
<h2>VAT formulas</h2>
<ul><li><strong>Add VAT:</strong> gross = net × 1.2 (at 20%)</li><li><strong>Remove VAT:</strong> net = gross ÷ 1.2 — not gross × 0.8, a common mistake.</li></ul>
<p>UK rates: standard 20%, reduced 5% (e.g. home energy, children's car seats), zero 0% (most food, books, children's clothes).</p>
""",
    [("Why isn't removing 20% VAT the same as taking 20% off?", "Because VAT is 20% of the net price, not the gross. £120 including VAT is £100 net, not £96.")],
    "Add or remove VAT at any rate.",
)

# ── Pension pot ──────────────────────────────────────────────
page(
    "pension-calculator",
    "Pension Calculator — How Big Will My Pension Pot Be?",
    "Pension Calculator",
    "Free pension calculator. Estimate your pension pot at retirement from your contributions, your employer's and investment growth, in today's money.",
    '<div class="grid">'
    + field("age", "Current age", 30, step="1")
    + field("ret", "Retirement age", 67, step="1")
    + field("pot", "Current pension pot", 15000)
    + field("sal", "Salary", 35000)
    + field("you", "Your contribution (%)", 5)
    + field("emp", "Employer contribution (%)", 3)
    + field("r", "Real investment return (%)", 4)
    + "</div>"
    '<div class="results">' + stat("fp", "Pot at retirement (today's money)") + stat("inc", "Annual income at 4% withdrawal") + stat("tc", "Total contributions") + "</div>"
    '<div class="chart" id="chart"></div>',
    """
App.bind(() => {
  const yrs = Math.max(0, Math.round(App.val("ret") - App.val("age"))), r = App.val("r") / 100;
  const add = App.val("sal") * (App.val("you") + App.val("emp")) / 100;
  let bal = App.val("pot"), paid = App.val("pot"); const L = [], C = [], G = [];
  for (let y = 1; y <= yrs; y++) { bal = bal * (1 + r) + add; paid += add; L.push(App.val("age") + y); C.push(paid); G.push(bal - paid); }
  App.set("fp", App.money(bal)); App.set("inc", App.money(bal * 0.04)); App.set("tc", App.money(paid));
  App.chart(document.getElementById("chart"), L, [
    { label: "Contributions", color: "var(--accent-2)", values: C },
    { label: "Growth", color: "var(--accent)", values: G },
  ]);
});
""",
    """
<h2>How this estimate works</h2>
<p>Each year, your pot grows by the real (after-inflation) return, and your and your employer's contributions are added. Using a real return keeps the result in today's money, so you can compare it with today's prices.</p>
<h2>Boosting your pension</h2>
<ul><li>Ask whether your employer matches extra contributions — it's free money.</li><li>Pension contributions get tax relief, so £80 from your pocket can become £100 in your pension (or more for higher-rate taxpayers).</li><li>Check fees: a 1% annual charge can reduce your final pot by a fifth or more.</li></ul>
<p>Most people will also get a State Pension on top, depending on their National Insurance record.</p>
""",
    [("What return should I assume?", "Many planners use 3–5% above inflation for a stock-heavy portfolio, lower for cautious funds. Returns aren't guaranteed.")],
    "Estimate your pension pot at retirement.",
)

# ── Investment return / CAGR ─────────────────────────────────
page(
    "investment-return-calculator",
    "Investment Return Calculator — CAGR & Annualised Return",
    "Investment Return (CAGR) Calculator",
    "Free investment return calculator. Work out your total return, compound annual growth rate (CAGR) and how long money takes to double.",
    '<div class="grid">' + field("s", "Starting value", 10000) + field("e", "Ending value", 18000) + field("y", "Years held", 6) + "</div>"
    '<div class="results">' + stat("tr", "Total return") + stat("cg", "Annualised return (CAGR)") + stat("db", "Years to double at this rate") + "</div>",
    """
App.bind(() => {
  const s = App.val("s"), e = App.val("e"), y = App.val("y");
  if (s <= 0 || y <= 0) return;
  const cagr = Math.pow(e / s, 1 / y) - 1;
  App.set("tr", `${App.num((e / s - 1) * 100, 2)}%`); App.set("cg", `${App.num(cagr * 100, 2)}%`);
  App.set("db", cagr > 0 ? `${App.num(Math.log(2) / Math.log(1 + cagr), 1)} years` : "—");
});
""",
    """
<h2>What is CAGR?</h2>
<p>The compound annual growth rate is the steady yearly return that would turn your starting value into your ending value. Formula: <code>CAGR = (end ÷ start)<sup>1/years</sup> − 1</code>. It smooths out ups and downs so you can compare investments held for different lengths of time.</p>
<h2>The rule of 72</h2>
<p>A quick shortcut: divide 72 by the annual return to estimate years to double. At 8%, money doubles in about 9 years.</p>
""",
    [("Should I include dividends?", "Yes — for a true total return, use an ending value that includes reinvested dividends or interest.")],
    "Total return, CAGR and doubling time.",
)

# ── Profit margin ────────────────────────────────────────────
page(
    "profit-margin-calculator",
    "Profit Margin & Markup Calculator",
    "Profit Margin & Markup Calculator",
    "Free profit margin calculator. Work out profit, margin and markup from cost and price, or the selling price needed for a target margin.",
    '<div class="grid">' + field("c", "Cost", 40) + field("p", "Selling price", 60) + "</div>"
    '<div class="results">' + stat("pr", "Profit") + stat("mg", "Margin") + stat("mk", "Markup") + "</div>"
    '<h2>Price for a target margin</h2><div class="grid">' + field("tm", "Target margin (%)", 40) + "</div>"
    '<div class="results">' + stat("tp", "Selling price needed") + "</div>",
    """
App.bind(() => {
  const c = App.val("c"), p = App.val("p"), tm = App.val("tm") / 100;
  App.set("pr", App.money(p - c, 2));
  App.set("mg", p ? `${App.num((p - c) / p * 100, 2)}%` : "—");
  App.set("mk", c ? `${App.num((p - c) / c * 100, 2)}%` : "—");
  App.set("tp", tm < 1 ? App.money(c / (1 - tm), 2) : "—");
});
""",
    """
<h2>Margin vs markup</h2>
<ul><li><strong>Margin</strong> = profit ÷ selling price. A £60 item costing £40 has a 33.3% margin.</li>
<li><strong>Markup</strong> = profit ÷ cost. The same item has a 50% markup.</li></ul>
<p>Confusing the two is a classic pricing mistake: adding a 40% markup does <em>not</em> give a 40% margin. To hit a target margin, price = cost ÷ (1 − margin).</p>
""",
    [("What's a good profit margin?", "It varies hugely by industry — from a few percent in groceries to 70%+ for software and digital products.")],
    "Profit, margin and markup from cost and price.",
)

# ── 50/30/20 budget ──────────────────────────────────────────
page(
    "budget-calculator",
    "50/30/20 Budget Calculator — Split Your Monthly Income",
    "50/30/20 Budget Calculator",
    "Free 50/30/20 budget calculator. Split your monthly take-home pay into needs, wants and savings — or set your own percentages.",
    '<div class="grid">' + field("i", "Monthly take-home pay", 2500) + field("n", "Needs (%)", 50) + field("w", "Wants (%)", 30) + field("s", "Savings & debt (%)", 20) + "</div>"
    '<div class="results">' + stat("on", "Needs") + stat("ow", "Wants") + stat("os", "Savings & debt repayment") + "</div>"
    '<p class="note" id="nt"></p>',
    """
App.bind(() => {
  const i = App.val("i"), n = App.val("n"), w = App.val("w"), s = App.val("s");
  App.set("on", App.money(i * n / 100)); App.set("ow", App.money(i * w / 100)); App.set("os", App.money(i * s / 100));
  App.set("nt", n + w + s === 100 ? `That's ${App.money(i * s / 100 * 12)} a year towards savings and debt.` : `Your percentages add up to ${n + w + s}% — adjust them to total 100%.`);
});
""",
    """
<h2>The 50/30/20 rule</h2>
<ul><li><strong>50% needs:</strong> rent or mortgage, bills, food, transport, minimum debt payments.</li>
<li><strong>30% wants:</strong> eating out, hobbies, subscriptions, holidays.</li>
<li><strong>20% savings:</strong> emergency fund, pension, investing and extra debt payments.</li></ul>
<p>In high-cost areas, needs often exceed 50% — a 60/20/20 or 70/20/10 split is fine. The point is to decide in advance where your money goes.</p>
""",
    [("Is 50/30/20 based on gross or net income?", "Net — your take-home pay after tax, NI and pension contributions.")],
    "Split income into needs, wants and savings.",
)

# ── Emergency fund ───────────────────────────────────────────
page(
    "emergency-fund-calculator",
    "Emergency Fund Calculator — How Much Should I Save?",
    "Emergency Fund Calculator",
    "Free emergency fund calculator. Work out how big your rainy-day fund should be and how long it will take to build.",
    '<div class="grid">' + field("e", "Essential monthly spending", 1500) + field("m", "Months of cover", 4, step="1")
    + field("h", "Already saved", 1000) + field("s", "Can save per month", 200) + "</div>"
    '<div class="results">' + stat("t", "Target fund") + stat("g", "Still to save") + stat("n", "Time to reach it") + "</div>",
    """
App.bind(() => {
  const t = App.val("e") * App.val("m"), g = Math.max(0, t - App.val("h")), s = App.val("s");
  App.set("t", App.money(t)); App.set("g", App.money(g));
  const n = s > 0 ? Math.ceil(g / s) : Infinity;
  App.set("n", g === 0 ? "Done!" : isFinite(n) ? `${Math.floor(n / 12)} yrs ${n % 12} mo` : "—");
});
""",
    """
<h2>How much emergency savings do you need?</h2>
<p>A common rule is three to six months of <em>essential</em> spending — rent or mortgage, bills, food and transport, not your full lifestyle. Aim higher if you're self-employed, have one household income or work in an unstable industry.</p>
<p>Keep it in an easy-access savings account: safe, separate from everyday spending and earning some interest.</p>
""",
    [("Should I invest my emergency fund?", "Generally no — its job is to be there when you need it, and investments can fall at exactly the wrong time.")],
    "How big your rainy-day fund should be.",
)

# ── Freelance day rate ───────────────────────────────────────
page(
    "freelance-rate-calculator",
    "Freelance Day Rate Calculator — What Should I Charge?",
    "Freelance Day Rate Calculator",
    "Free freelance rate calculator. Work out the day rate and hourly rate you need to charge to hit your target income after expenses and time off.",
    '<div class="grid">' + field("t", "Target annual income (before tax)", 45000) + field("x", "Annual business expenses", 3000)
    + field("hol", "Weeks off per year (holiday, sickness)", 7) + field("u", "Billable share of working days (%)", 70) + field("h", "Hours per day", 7.5) + "</div>"
    '<div class="results">' + stat("dr", "Day rate") + stat("hr", "Hourly rate") + stat("bd", "Billable days per year") + "</div>",
    """
App.bind(() => {
  const days = Math.max(1, (52 - App.val("hol")) * 5 * App.val("u") / 100), need = App.val("t") + App.val("x");
  App.set("dr", App.money(need / days)); App.set("hr", App.money(need / days / (App.val("h") || 1), 2)); App.set("bd", App.num(days, 0));
});
""",
    """
<h2>Why freelance rates look high</h2>
<p>Employees are paid for holidays, sick days and admin time, and their employer covers equipment, pension and NI. As a freelancer you fund all of that yourself, and not every working day is billable — you'll spend time finding clients, invoicing and learning.</p>
<p>That's why a freelancer typically needs a day rate of roughly 1/200th to 1/150th of an equivalent salary.</p>
""",
    [("What billable percentage is realistic?", "Many freelancers bill 60–75% of working days; newer freelancers often less while building a client base.")],
    "The day rate you need to hit your income target.",
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
                                           "Free, private finance calculators: UK take-home pay, stamp duty, mortgage, compound interest, pension, debt payoff, budgeting and more. No sign-up.",
                                           "", home))

    privacy = """<h1>Privacy</h1>
<p>All calculations happen in your browser. We don't collect, store or transmit the numbers you enter.</p>
<p>We may count anonymous page visits with a cookie-free analytics service (Cloudflare Web Analytics or GoatCounter) to see which pages are useful. No personal data is collected.</p>
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
