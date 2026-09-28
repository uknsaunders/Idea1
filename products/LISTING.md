# Digital products: Gumroad or Payhip listings

Two ready-to-sell products in `products/out/`:

| File | Product | Suggested price |
|---|---|---|
| `UK-Budget-Planner.xlsx` | UK Budget Planner spreadsheet (Excel, Google Sheets, Numbers) | £5 |
| `Money-Planner-Pack-A4.pdf` | Printable Money Planner Pack, 9 A4 pages | £3 |
| both | **Bundle** | £6.50 |

Rebuild with `python3 products/make_budget_xlsx.py` and `python3 products/make_planner_pdf.py`.

## Where to sell (free to list)

- **Payhip** (payhip.com): free plan, 5% fee per sale, handles UK/EU VAT for you. **Recommended.**
- **Gumroad** (gumroad.com): free to list, 10% fee per sale.
- *Etsy* has the most buyers for printables, but charges $0.20 per listing (the only non-free option here).

Setup: create an account, connect PayPal or your bank, click **New product → Digital download**, upload the file, then paste the text below.
You'll also want a **cover image** for each product: take a screenshot of the first page, or ask Claude to generate mock-up images.

---

## 1. UK Budget Planner (spreadsheet)

**Title:** UK Budget Planner Spreadsheet: Monthly Budget, Expense Tracker, Savings & Debt Tracker (Excel & Google Sheets)

**Description:**
> Take control of your money with a simple, automatic budget spreadsheet made for UK households.
>
> **What's inside (6 tabs):**
> - **Monthly Budget:** 20 UK categories (council tax, energy, broadband and more) with planned vs actual, and a built-in 50/30/20 check
> - **Expense Tracker:** log purchases with a category drop-down; your budget updates automatically
> - **Savings Goals:** enter a target and a date to see exactly how much to save each month
> - **Debt Tracker:** see how long each debt takes to clear and what it costs in interest
> - **Year Overview:** track income, spending and savings rate month by month
> - Clear colour-coding (yellow = type here) and example figures to get you started
>
> Works in Microsoft Excel, Google Sheets (free) and Apple Numbers. Instant download, no subscription.

**Tags:** budget spreadsheet, uk budget planner, excel budget template, google sheets budget, expense tracker, savings tracker, debt tracker, 50 30 20 budget

## 2. Money Planner Pack (printable PDF)

**Title:** Printable Money Planner: Budget, Bill Tracker, Debt Payoff & £1,000 Savings Challenge (A4 PDF)

**Description:**
> Nine beautifully simple printable pages to plan, track and grow your money, month after month.
>
> - Monthly Budget
> - Expense Tracker
> - Bill Tracker (12-month tick grid)
> - Debt Payoff Tracker: colour in the boxes as your debt disappears
> - £1,000 Savings Challenge: 60 circles to colour in
> - Savings Goals thermometers
> - No-Spend Challenge calendar
> - Monthly Review prompts
>
> A4 PDF. Print at home as many times as you like, or fill in on a tablet with any PDF annotation app.

**Tags:** printable budget planner, savings challenge, debt payoff tracker, bill tracker printable, budget binder, money planner, no spend challenge

---

## Cross-promotion (free)

- Once the products are live, add them to `site/assets/config.js` → `affiliates`, e.g.
  `{ title: "UK Budget Planner spreadsheet", text: "The spreadsheet version of these calculators. £5, instant download.", url: "https://payhip.com/b/XXXX" }`
  They'll then appear on every calculator page. The budget, debt and savings calculators are the best fit.
- **Pinterest:** pin each page image with its product link (printables are one of Pinterest's biggest categories).
