#!/usr/bin/env python3
"""Build the printable 'Money Planner Pack' → products/out/Money-Planner-Pack-A4.pdf"""
import pathlib
import random

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

OUT = pathlib.Path(__file__).parent / "out"
FD = "/usr/share/fonts/truetype/liberation/"
pdfmetrics.registerFont(TTFont("Body", FD + "LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Bold", FD + "LiberationSans-Bold.ttf"))
W, H = A4
M = 15 * mm
TEAL, SOFT, LINE, INK, MUTED = HexColor("#0F7B5F"), HexColor("#E3F4EE"), HexColor("#B8C2CC"), HexColor("#1C2330"), HexColor("#5B6475")


def title(c, text, sub=""):
    c.setFillColor(TEAL)
    c.rect(0, H - 30 * mm, W, 30 * mm, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont("Bold", 24)
    c.drawString(M, H - 17 * mm, text)
    if sub:
        c.setFont("Body", 10.5)
        c.drawString(M, H - 24 * mm, sub)
    c.setFont("Body", 10)
    c.drawRightString(W - M, H - 17 * mm, "Month: ____________")  # printed on every page so sheets can be reused
    c.setFillColor(INK)


def footer(c):
    c.setFont("Body", 8)
    c.setFillColor(MUTED)
    c.drawCentredString(W / 2, 8 * mm, "Money Planner Pack · for personal use · print as many copies as you like")


def table(c, x, y_top, cols, rows, row_h=8 * mm, head_fill=TEAL, prefill=None):
    """cols = [(label, width_mm)]; draws a header row and `rows` empty ruled rows."""
    total = sum(w for _, w in cols) * mm
    c.setFillColor(head_fill)
    c.rect(x, y_top - row_h, total, row_h, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont("Bold", 9.5)
    cx = x
    for lab, w in cols:
        c.drawCentredString(cx + w * mm / 2, y_top - row_h + 2.8 * mm, lab)
        cx += w * mm
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    for r in range(rows + 1):
        yy = y_top - row_h * (r + 1)
        c.line(x, yy, x + total, yy)
    cx = x
    for _, w in cols[:-1]:
        cx += w * mm
        c.line(cx, y_top - row_h, cx, y_top - row_h * (rows + 1))
    c.rect(x, y_top - row_h * (rows + 1), total, row_h * (rows + 1), stroke=1, fill=0)
    if prefill:
        c.setFillColor(INK)
        c.setFont("Body", 9.5)
        for r, text in enumerate(prefill):
            c.drawString(x + 2 * mm, y_top - row_h * (r + 2) + 2.6 * mm, text)
    return y_top - row_h * (rows + 1)


def cover(c):
    c.setFillColor(TEAL)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont("Bold", 46)
    c.drawCentredString(W / 2, H * .62, "Money Planner")
    c.setFont("Body", 22)
    c.drawCentredString(W / 2, H * .62 - 16 * mm, "Printable budget & savings pack")
    c.setFont("Body", 12)
    items = ["Monthly Budget", "Expense Tracker", "Bill Tracker", "Debt Payoff Tracker", "£1,000 Savings Challenge",
             "Savings Goals", "No-Spend Challenge", "Monthly Review"]
    for i, it in enumerate(items):
        c.drawCentredString(W / 2, H * .45 - i * 7 * mm, "•  " + it)
    c.setFont("Body", 10)
    c.drawCentredString(W / 2, 18 * mm, "A4 · print at home · reuse every month")


def budget(c):
    title(c, "Monthly Budget", "Plan every pound before the month starts, then fill in what you actually spent.")
    y = table(c, M, H - 38 * mm, [("Income", 110), ("Planned", 35), ("Actual", 35)], 3,
              prefill=["Take-home pay", "Other income", "TOTAL INCOME"])
    cats = ["Rent / mortgage", "Council tax", "Energy", "Water", "Phone & broadband", "Groceries", "Transport",
            "Insurance", "Debt payments", "Childcare", "Eating out", "Subscriptions", "Clothes", "Entertainment",
            "Gifts", "Savings", "Pension / investing", "Other", "", "", "TOTAL SPENDING"]
    y = table(c, M, y - 8 * mm, [("Expense", 110), ("Planned", 35), ("Actual", 35)], len(cats), row_h=7.6 * mm, prefill=cats)
    c.setFillColor(SOFT)
    c.roundRect(M, y - 22 * mm, W - 2 * M, 16 * mm, 3 * mm, stroke=0, fill=1)
    c.setFillColor(INK)
    c.setFont("Bold", 11)
    c.drawString(M + 5 * mm, y - 12 * mm, "Income − spending = left over:  £ __________")
    c.drawString(M + 105 * mm, y - 12 * mm, "Goal for next month: ________________")


def expenses(c):
    title(c, "Expense Tracker", "Write down every purchase. Small spends add up fast!")
    table(c, M, H - 38 * mm, [("Date", 22), ("Description", 78), ("Category", 45), ("Amount", 35)], 30, row_h=7.9 * mm)


def bills(c):
    title(c, "Bill Tracker", "Tick each bill as it's paid, every month of the year.")
    months = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
    table(c, M, H - 38 * mm, [("Bill", 50), ("Due", 16), ("£", 18)] + [(m, 8) for m in months], 28, row_h=8.3 * mm)


def debt(c):
    title(c, "Debt Payoff Tracker", "Colour in a box for every chunk you pay off. Watch the debt disappear!")
    y = H - 40 * mm
    for k in range(3):
        c.setFillColor(INK)
        c.setFont("Bold", 11)
        c.drawString(M, y, "Debt: ______________________   Starting balance: £ ________   Each box = £ ______")
        size, per_row = 8.4 * mm, 20
        for i in range(40):
            bx = M + (i % per_row) * (size + 0.6 * mm)
            by = y - 6 * mm - (i // per_row + 1) * (size + 0.6 * mm)
            c.setStrokeColor(TEAL)
            c.setLineWidth(0.8)
            c.roundRect(bx, by, size, size, 1.5 * mm, stroke=1, fill=0)
            c.setFont("Body", 6.5)
            c.setFillColor(MUTED)
            c.drawCentredString(bx + size / 2, by + size / 2 - 2, str(i + 1))
        y -= 33 * mm
        c.setFont("Body", 9.5)
        c.setFillColor(INK)
        c.drawString(M, y + 4 * mm, "Interest rate: ______ %     Minimum payment: £ ______     Target payoff date: ____________")
        y -= 16 * mm
    table(c, M, y + 4 * mm, [("Date", 30), ("Payment", 35), ("New balance", 40), ("Notes", 75)], 6, row_h=7.5 * mm)


def challenge(c):
    title(c, "£1,000 Savings Challenge", "Each time you save, colour in a circle. Fill them all to save £1,000.")
    amounts = [5] * 10 + [10] * 18 + [15] * 8 + [20] * 10 + [25] * 6 + [30] * 4 + [40] * 2 + [50] * 2
    assert sum(amounts) == 1000 and len(amounts) == 60, sum(amounts)
    random.Random(3).shuffle(amounts)
    cols, r = 6, 9.5 * mm
    gx = (W - (cols - 1) * 2.9 * r) / 2
    for i, a in enumerate(amounts):
        x = gx + (i % cols) * 2.9 * r
        y = H - 50 * mm - (i // cols) * 2.25 * r
        c.setStrokeColor(TEAL)
        c.setLineWidth(1.2)
        c.circle(x, y, r, stroke=1, fill=0)
        c.setFillColor(TEAL)
        c.setFont("Bold", 13)
        c.drawCentredString(x, y - 4.5, f"£{a}")
    c.setFillColor(INK)
    c.setFont("Body", 10)
    c.drawCentredString(W / 2, 16 * mm, "Started: ____________     Finished: ____________     What I'm saving for: ______________________")


def goals(c):
    title(c, "Savings Goals", "Four goals, four thermometers. Shade in your progress as you save.")
    for k in range(4):
        x = M + (k % 2) * (W / 2 - M / 2)
        y = H - 45 * mm - (k // 2) * 118 * mm
        c.setFillColor(INK)
        c.setFont("Bold", 11)
        c.drawString(x, y, "Goal: ______________________")
        c.setFont("Body", 10)
        c.drawString(x, y - 7 * mm, "Target: £ ________   By: __________")
        tx, ttop, th, tw = x + 12 * mm, y - 14 * mm, 88 * mm, 14 * mm
        c.setStrokeColor(TEAL)
        c.setLineWidth(1.4)
        c.roundRect(tx, ttop - th, tw, th, tw / 2, stroke=1, fill=0)
        c.circle(tx + tw / 2, ttop - th - 5 * mm, 10 * mm, stroke=1, fill=0)
        for p in range(0, 101, 10):
            ly = ttop - th + 6 * mm + (th - 12 * mm) * p / 100
            c.setLineWidth(0.6)
            c.line(tx + tw, ly, tx + tw + 4 * mm, ly)
            c.setFont("Body", 8)
            c.drawString(tx + tw + 5 * mm, ly - 3, f"{p}%   £ ______")


def nospend(c):
    title(c, "No-Spend Challenge", "Cross off each day you spend nothing beyond essentials. How long can you go?")
    size = (W - 2 * M) / 7
    for i in range(31):
        x = M + (i % 7) * size
        y = H - 42 * mm - (i // 7 + 1) * size
        c.setStrokeColor(LINE)
        c.setLineWidth(0.8)
        c.rect(x, y, size, size, stroke=1, fill=0)
        c.setFillColor(TEAL)
        c.setFont("Bold", 14)
        c.drawString(x + 3 * mm, y + size - 7 * mm, str(i + 1))
    c.setFillColor(INK)
    c.setFont("Bold", 11)
    y = H - 42 * mm - 5 * size - 12 * mm
    c.drawString(M, y, "My rules (what counts as essential?)")
    c.setStrokeColor(LINE)
    for k in range(4):
        c.line(M, y - (k + 1) * 9 * mm, W - M, y - (k + 1) * 9 * mm)
    c.drawString(M, y - 48 * mm, "Longest streak: ______ days        Money saved: £ __________")


def review(c):
    title(c, "Monthly Review", "Five minutes at the end of each month keeps your plan on track.")
    table(c, M, H - 38 * mm, [("Summary", 110), ("£", 70)], 5,
          prefill=["Total income", "Total spent", "Total saved", "Debt paid off", "Net worth change"])
    prompts = ["What went well this month?", "Where did I overspend, and why?", "One thing I'll change next month:",
               "Upcoming costs to plan for (birthdays, renewals, holidays):"]
    y = H - 100 * mm
    for p in prompts:
        c.setFillColor(TEAL)
        c.setFont("Bold", 12)
        c.drawString(M, y, p)
        c.setStrokeColor(LINE)
        for k in range(4):
            c.line(M, y - (k + 1) * 9 * mm, W - M, y - (k + 1) * 9 * mm)
        y -= 48 * mm


def main():
    OUT.mkdir(exist_ok=True)
    path = OUT / "Money-Planner-Pack-A4.pdf"
    c = canvas.Canvas(str(path), pagesize=A4, initialFontName="Body")
    c.setTitle("Money Planner Pack")
    for fn in (cover, budget, expenses, bills, debt, challenge, goals, nospend, review):
        fn(c)
        if fn is not cover:
            footer(c)
        c.showPage()
    c.save()
    print(path)


if __name__ == "__main__":
    main()
