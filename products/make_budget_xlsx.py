#!/usr/bin/env python3
"""Build the 'UK Budget Planner' spreadsheet product → products/out/UK-Budget-Planner.xlsx"""
import pathlib

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, DataBarRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

OUT = pathlib.Path(__file__).parent / "out"
GBP = '£#,##0.00;[Red]-£#,##0.00;"-"'
PCT = '0.0%;-0.0%;"-"'
F = "Arial"
TEAL, TEAL_SOFT, INPUT, GREY = "0F7B5F", "E3F4EE", "FFF4C2", "F2F2F2"
thin = Side(style="thin", color="D0D5DD")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)

CATEGORIES = [
    ("Rent / mortgage", "Need", 950), ("Council tax", "Need", 150), ("Energy (gas & electric)", "Need", 120),
    ("Water", "Need", 40), ("Phone & broadband", "Need", 55), ("Groceries", "Need", 320),
    ("Transport / fuel", "Need", 150), ("Insurance", "Need", 45), ("Childcare", "Need", 0),
    ("Minimum debt payments", "Need", 60), ("Eating out & takeaways", "Want", 120), ("Subscriptions", "Want", 35),
    ("Clothes", "Want", 50), ("Hobbies & entertainment", "Want", 80), ("Gifts", "Want", 30),
    ("Holidays", "Want", 45), ("Emergency fund", "Savings", 150), ("Pension top-up", "Savings", 50),
    ("ISA / investing", "Savings", 100), ("Extra debt repayment", "Savings", 50),
]


def style_title(ws, text, sub):
    ws["A1"] = text
    ws["A1"].font = Font(name=F, size=18, bold=True, color=TEAL)
    ws["A2"] = sub
    ws["A2"].font = Font(name=F, size=10, italic=True, color="666666")
    ws.sheet_view.showGridLines = False


def header(ws, row, labels, col=1):
    for i, lab in enumerate(labels):
        c = ws.cell(row=row, column=col + i, value=lab)
        c.font = Font(name=F, bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=TEAL)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BOX


def cell(ws, ref, value=None, fmt=None, inp=False, bold=False, fill=None):
    c = ws[ref]
    if value is not None:
        c.value = value
    c.font = Font(name=F, bold=bold, color="0000FF" if inp else "000000")
    if fmt:
        c.number_format = fmt
    if inp:
        c.fill = PatternFill("solid", fgColor=INPUT)
    elif fill:
        c.fill = PatternFill("solid", fgColor=fill)
    c.border = BOX
    return c


def widths(ws, w):
    for col, width in w.items():
        ws.column_dimensions[col].width = width


def main():
    OUT.mkdir(exist_ok=True)
    wb = Workbook()

    # ── Start Here ─────────────────────────────────────────────
    ws = wb.active
    ws.title = "Start Here"
    style_title(ws, "UK Budget Planner", "Plan your month, track every purchase, and hit your savings goals.")
    rows = [
        ("How to use this planner", True),
        ("1. Monthly Budget: enter your income and a budget for each category (yellow cells).", False),
        ("2. Expense Tracker: log each purchase. Pick its category from the drop-down and the Budget tab fills in 'Actual' automatically.", False),
        ("3. Savings Goals: list what you're saving for and see how much to put aside each month.", False),
        ("4. Debt Tracker: see how long each debt will take to clear and what it will cost in interest.", False),
        ("5. Year Overview: record each month's totals to watch your progress over the year.", False),
        ("", False),
        ("Colour key", True),
        ("Yellow cells with blue text = type your own numbers here", False),
        ("White cells with black text = calculated automatically (formulas, don't overwrite)", False),
        ("", False),
        ("The example figures are there to show the format. Replace them with your own.", False),
        ("Tip: to rename or add categories, edit the list on the Monthly Budget tab. The drop-downs update automatically.", False),
        ("Works in Microsoft Excel, Google Sheets (File → Import) and Apple Numbers.", False),
    ]
    for i, (t, b) in enumerate(rows, 4):
        ws.cell(row=i, column=1, value=t).font = Font(name=F, size=12 if b else 11, bold=b, color=TEAL if b else "000000")
    ws["A12"].fill = PatternFill("solid", fgColor=INPUT)
    ws["A12"].font = Font(name=F, color="0000FF")
    widths(ws, {"A": 120})

    # ── Monthly Budget ─────────────────────────────────────────
    b = wb.create_sheet("Monthly Budget")
    style_title(b, "Monthly Budget", "Yellow = your numbers. 'Actual' is pulled from the Expense Tracker tab.")
    cell(b, "A4", "Income", bold=True, fill=TEAL_SOFT)
    cell(b, "B4", "Amount", bold=True, fill=TEAL_SOFT)
    for r, (lab, v) in enumerate([("Take-home pay", 2600), ("Partner's take-home pay", 0), ("Other income", 0)], 5):
        cell(b, f"A{r}", lab, inp=True)
        cell(b, f"B{r}", v, GBP, inp=True)
    cell(b, "A8", "Total income", bold=True)
    cell(b, "B8", "=SUM(B5:B7)", GBP, bold=True)

    header(b, 10, ["Category", "Type", "Budget", "Actual", "Left to spend", "% of budget used"])
    first = 11
    last = first + len(CATEGORIES) - 1
    for i, (name, typ, amt) in enumerate(CATEGORIES):
        r = first + i
        cell(b, f"A{r}", name, inp=True)
        cell(b, f"B{r}", typ, inp=True)
        cell(b, f"C{r}", amt, GBP, inp=True)
        cell(b, f"D{r}", f"=SUMIFS('Expense Tracker'!$D:$D,'Expense Tracker'!$C:$C,A{r})", GBP)
        cell(b, f"E{r}", f"=C{r}-D{r}", GBP)
        cell(b, f"F{r}", f"=IF(C{r}=0,0,D{r}/C{r})", PCT)
    t = last + 1
    cell(b, f"A{t}", "Total", bold=True, fill=GREY)
    cell(b, f"B{t}", "", fill=GREY)
    for col in "CDE":
        cell(b, f"{col}{t}", f"=SUM({col}{first}:{col}{last})", GBP, bold=True, fill=GREY)
    cell(b, f"F{t}", f"=IF(C{t}=0,0,D{t}/C{t})", PCT, bold=True, fill=GREY)
    b.conditional_formatting.add(f"E{first}:E{last}", CellIsRule(operator="lessThan", formula=["0"], font=Font(name=F, color="C00000", bold=True)))
    b.conditional_formatting.add(f"F{first}:F{last}", DataBarRule(start_type="num", start_value=0, end_type="num", end_value=1, color="8FD3BD"))
    dv = DataValidation(type="list", formula1='"Need,Want,Savings"', allow_blank=True)
    b.add_data_validation(dv)
    dv.add(f"B{first}:B{last}")

    s = t + 2
    cell(b, f"A{s}", "Unallocated income (income − total budget)", bold=True)
    cell(b, f"C{s}", f"=B8-C{t}", GBP, bold=True)
    b.conditional_formatting.add(f"C{s}", CellIsRule(operator="lessThan", formula=["0"], font=Font(name=F, color="C00000", bold=True)))
    header(b, s + 2, ["50/30/20 check", "Target %", "Your budget", "Your %", "Target amount"])
    for k, (typ, pct) in enumerate([("Need", 0.5), ("Want", 0.3), ("Savings", 0.2)]):
        r = s + 3 + k
        cell(b, f"A{r}", typ)
        cell(b, f"B{r}", pct, PCT, inp=True)
        cell(b, f"C{r}", f"=SUMIFS($C${first}:$C${last},$B${first}:$B${last},A{r})", GBP)
        cell(b, f"D{r}", f"=IF($B$8=0,0,C{r}/$B$8)", PCT)
        cell(b, f"E{r}", f"=$B$8*B{r}", GBP)
    cell(b, f"A{s + 6}", "The 50/30/20 split is a guide: 50% needs, 30% wants, 20% savings and extra debt repayment. Adjust the targets to suit you.").font = Font(name=F, italic=True, size=9, color="666666")
    b.cell(row=s + 6, column=1).border = Border()
    widths(b, {"A": 42, "B": 12, "C": 15, "D": 15, "E": 16, "F": 16})
    b.freeze_panes = "A11"

    # ── Expense Tracker ────────────────────────────────────────
    e = wb.create_sheet("Expense Tracker")
    style_title(e, "Expense Tracker", "Log every purchase. The category drop-down links to your Monthly Budget.")
    header(e, 4, ["Date", "Description", "Category", "Amount", "Notes"])
    examples = [("2026-10-01", "Rent", "Rent / mortgage", 950), ("2026-10-02", "Weekly shop", "Groceries", 78.45),
                ("2026-10-03", "Train tickets", "Transport / fuel", 32.10), ("2026-10-05", "Pizza night", "Eating out & takeaways", 24.99)]
    import datetime
    for r in range(5, 505):
        for col in "ABCDE":
            cell(e, f"{col}{r}", inp=True)
        e[f"A{r}"].number_format = "DD/MM/YYYY"
        e[f"D{r}"].number_format = GBP
    for i, (d, desc, cat, amt) in enumerate(examples, 5):
        e[f"A{i}"] = datetime.date.fromisoformat(d)
        e[f"B{i}"], e[f"C{i}"], e[f"D{i}"] = desc, cat, amt
    dv2 = DataValidation(type="list", formula1=f"='Monthly Budget'!$A${first}:$A${last}", allow_blank=True)
    e.add_data_validation(dv2)
    dv2.add("C5:C504")
    widths(e, {"A": 13, "B": 34, "C": 28, "D": 13, "E": 30})
    e.freeze_panes = "A5"

    # ── Savings Goals ──────────────────────────────────────────
    g = wb.create_sheet("Savings Goals")
    style_title(g, "Savings Goals", "Enter a target and a date. The sheet works out what to save each month.")
    cell(g, "A4", "Today's date", bold=True)
    cell(g, "B4", "=TODAY()", "DD/MM/YYYY")
    header(g, 6, ["Goal", "Target", "Saved so far", "Still to save", "Progress", "Target date", "Months left", "Save per month"])
    goals = [("Emergency fund", 6000, 1500, "2027-06-30"), ("Summer holiday", 1500, 300, "2027-05-31"), ("New car deposit", 3000, 0, "2028-01-31")]
    for i in range(10):
        r = 7 + i
        for col, fmt in zip("ABCF", [None, GBP, GBP, "DD/MM/YYYY"]):
            cell(g, f"{col}{r}", None, fmt, inp=True)
        if i < len(goals):
            name, tgt, saved, date = goals[i]
            g[f"A{r}"], g[f"B{r}"], g[f"C{r}"], g[f"F{r}"] = name, tgt, saved, datetime.date.fromisoformat(date)
        cell(g, f"D{r}", f'=IF(B{r}="","",MAX(0,B{r}-C{r}))', GBP)
        cell(g, f"E{r}", f'=IF(OR(B{r}="",B{r}=0),"",MIN(1,C{r}/B{r}))', PCT)
        cell(g, f"G{r}", f'=IF(F{r}="","",MAX(1,(YEAR(F{r})-YEAR($B$4))*12+MONTH(F{r})-MONTH($B$4)))', "0")
        cell(g, f"H{r}", f'=IF(OR(D{r}="",G{r}=""),"",D{r}/G{r})', GBP)
    g.conditional_formatting.add("E7:E16", DataBarRule(start_type="num", start_value=0, end_type="num", end_value=1, color="8FD3BD"))
    cell(g, "A17", "Total", bold=True, fill=GREY)
    for col in "BCDH":
        cell(g, f"{col}17", f"=SUM({col}7:{col}16)", GBP, bold=True, fill=GREY)
    widths(g, {"A": 28, "B": 13, "C": 14, "D": 14, "E": 12, "F": 13, "G": 12, "H": 15})

    # ── Debt Tracker ───────────────────────────────────────────
    d = wb.create_sheet("Debt Tracker")
    style_title(d, "Debt Tracker", "See how long each debt takes to clear at your monthly payment, and the interest it costs.")
    header(d, 4, ["Debt", "Balance", "APR", "Monthly payment", "Months to clear", "Total interest", "Status"])
    debts = [("Credit card", 2400, 0.249, 120), ("Car loan", 6500, 0.079, 210), ("Overdraft", 500, 0.399, 50)]
    for i in range(8):
        r = 5 + i
        for col, fmt in zip("ABCD", [None, GBP, PCT, GBP]):
            cell(d, f"{col}{r}", None, fmt, inp=True)
        if i < len(debts):
            d[f"A{r}"], d[f"B{r}"], d[f"C{r}"], d[f"D{r}"] = debts[i]
        # Monthly rate = APR/12 (simple approximation used by most lenders' illustrations)
        cell(d, f"E{r}", f'=IF(OR(B{r}="",D{r}=""),"",IF(B{r}*C{r}/12>=D{r},"Never",ROUNDUP(IF(C{r}=0,B{r}/D{r},NPER(C{r}/12,-D{r},B{r})),0)))', "0")
        cell(d, f"F{r}", f'=IF(OR(E{r}="",E{r}="Never"),"",MAX(0,IF(C{r}=0,0,NPER(C{r}/12,-D{r},B{r})*D{r}-B{r})))', GBP)
        cell(d, f"G{r}", f'=IF(E{r}="","",IF(E{r}="Never","Payment too low: increase it",IF(E{r}<=12,"Clear within a year","Clear in "&ROUND(E{r}/12,1)&" years")))')
    cell(d, "A13", "Total", bold=True, fill=GREY)
    for col in "BDF":
        cell(d, f"{col}13", f"=SUM({col}5:{col}12)", GBP, bold=True, fill=GREY)
    cell(d, "A15", "Tip: pay minimums on everything, then put any extra towards the highest-APR debt first (the 'avalanche' method).").border = Border()
    d["A15"].font = Font(name=F, italic=True, size=9, color="666666")
    widths(d, {"A": 24, "B": 13, "C": 9, "D": 16, "E": 15, "F": 15, "G": 30})

    # ── Year Overview ──────────────────────────────────────────
    y = wb.create_sheet("Year Overview")
    style_title(y, "Year Overview", "At the end of each month, copy in your totals to track the year.")
    header(y, 4, ["Month", "Income", "Spent", "Saved", "Savings rate", "Running total saved"])
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    for i, m in enumerate(months):
        r = 5 + i
        cell(y, f"A{r}", m)
        cell(y, f"B{r}", 2600 if i == 0 else None, GBP, inp=True)
        cell(y, f"C{r}", 2310 if i == 0 else None, GBP, inp=True)
        cell(y, f"D{r}", f'=IF(B{r}="","",B{r}-C{r})', GBP)
        cell(y, f"E{r}", f'=IF(OR(B{r}="",B{r}=0),"",D{r}/B{r})', PCT)
        cell(y, f"F{r}", f'=IF(D{r}="","",SUM($D$5:D{r}))', GBP)
    cell(y, "A17", "Year total", bold=True, fill=GREY)
    for col in "BCD":
        cell(y, f"{col}17", f"=SUM({col}5:{col}16)", GBP, bold=True, fill=GREY)
    cell(y, "E17", '=IF(B17=0,"",D17/B17)', PCT, bold=True, fill=GREY)
    cell(y, "F17", "", fill=GREY)
    widths(y, {"A": 14, "B": 14, "C": 14, "D": 14, "E": 14, "F": 20})

    for sh in wb.worksheets:
        sh.sheet_properties.tabColor = TEAL
    path = OUT / "UK-Budget-Planner.xlsx"
    wb.save(path)
    print(path)


if __name__ == "__main__":
    main()
