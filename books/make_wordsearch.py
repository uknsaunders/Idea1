#!/usr/bin/env python3
"""Build a KDP-ready large-print word search book (interior PDF + full-wrap cover PDF).

Usage:  python3 books/make_wordsearch.py
Output: books/out/wordsearch-interior.pdf, books/out/wordsearch-cover.pdf, books/out/LISTING.md

Specs: 8.5 x 11 in trim, no bleed (interior), black & white, white paper.
"""
import pathlib
import random

from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from wordsearch_themes import THEMES

TITLE = "Great British Large Print Word Search"
SUBTITLE = "50 Themed Puzzles for Adults & Seniors"
AUTHOR = "Seaside Puzzle Press"  # pen name / imprint shown on the cover; change freely
YEAR = 2026
SIZE = 15                          # grid is SIZE x SIZE
W, H = 8.5 * inch, 11 * inch
MARGIN = 0.75 * inch               # comfortably above KDP's 0.375in inside / 0.25in outside minimums
DIRS = [(0, 1), (1, 0), (1, 1), (-1, 1)]  # right, down, diagonal down-right, diagonal up-right (no backwards words)
OUT = pathlib.Path(__file__).parent / "out"
# KDP requires embedded fonts, so use TrueType files (Liberation Sans, SIL Open Font Licence) rather than built-in Helvetica
FONT_DIR = "/usr/share/fonts/truetype/liberation/"
pdfmetrics.registerFont(TTFont("Body", FONT_DIR + "LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Body-Bold", FONT_DIR + "LiberationSans-Bold.ttf"))
FONT, BOLD = "Body", "Body-Bold"


def unique(grid, words):
    """True if every word occurs exactly once reading in the puzzle's forward directions (so solutions are unambiguous)."""
    lines = ["".join(row) for row in grid] + ["".join(grid[y][x] for y in range(SIZE)) for x in range(SIZE)]
    for d in range(-SIZE + 1, SIZE):
        lines.append("".join(grid[y][y - d] for y in range(SIZE) if 0 <= y - d < SIZE))  # down-right
        lines.append("".join(grid[y][d + SIZE - 1 - y] for y in range(SIZE) if 0 <= d + SIZE - 1 - y < SIZE)[::-1])  # up-right
    return all(sum(line.count(w) for line in lines) == 1 for w in words)


def make_grid(words, rnd):
    for _ in range(500):
        grid = [[None] * SIZE for _ in range(SIZE)]
        placed = {}
        ok = True
        for w in sorted(words, key=len, reverse=True):
            spots = []
            for dr, dc in DIRS:
                for r in range(SIZE):
                    for c in range(SIZE):
                        er, ec = r + dr * (len(w) - 1), c + dc * (len(w) - 1)
                        if not (0 <= er < SIZE and 0 <= ec < SIZE):
                            continue
                        cells = [(r + dr * i, c + dc * i) for i in range(len(w))]
                        if all(grid[y][x] in (None, w[i]) for i, (y, x) in enumerate(cells)):
                            overlap = sum(grid[y][x] is not None for y, x in cells)
                            spots.append((overlap, rnd.random(), cells))
            if not spots:
                ok = False
                break
            # Mostly random placement, with a mild preference for crossing other words
            spots.sort(key=lambda s: (-min(s[0], 1) if rnd.random() < 0.3 else 0, s[1]))
            cells = spots[0][2]
            for i, (y, x) in enumerate(cells):
                grid[y][x] = w[i]
            placed[w] = cells
        if ok:
            letters = "".join(words)
            empty = [(y, x) for y in range(SIZE) for x in range(SIZE) if grid[y][x] is None]
            for _ in range(200):  # reshuffle only the filler letters until every word appears exactly once
                for y, x in empty:
                    grid[y][x] = rnd.choice(letters)  # puzzle's own letters, so real words don't stand out
                if unique(grid, words):
                    return grid, placed
    raise RuntimeError(f"Could not place words: {words}")


def centred(c, text, y, font, size, colour=black):
    c.setFont(font, size)
    c.setFillColor(colour)
    c.drawCentredString(W / 2, y, text)


def page_number(c, n):
    c.setFont(FONT, 11)
    c.setFillColor(black)
    c.drawCentredString(W / 2, 0.45 * inch, str(n))


def draw_grid(c, grid, x0, y_top, cell, font_size, placed=None):
    if placed:
        c.setStrokeColor(HexColor("#9a9a9a"))
        c.setLineWidth(cell * 0.62)
        c.setLineCap(1)
        for cells in placed.values():
            (r1, c1), (r2, c2) = cells[0], cells[-1]
            c.line(x0 + (c1 + .5) * cell, y_top - (r1 + .5) * cell, x0 + (c2 + .5) * cell, y_top - (r2 + .5) * cell)
    c.setStrokeColor(black)
    c.setLineWidth(1.2)
    c.rect(x0 - cell * .25, y_top - SIZE * cell - cell * .25, SIZE * cell + cell * .5, SIZE * cell + cell * .5)
    c.setFillColor(black)
    c.setFont(BOLD, font_size)
    for r, row in enumerate(grid):
        for col, ch in enumerate(row):
            c.drawCentredString(x0 + (col + .5) * cell, y_top - (r + .5) * cell - font_size * .35, ch)


def interior(puzzles):
    path = OUT / "wordsearch-interior.pdf"
    c = canvas.Canvas(str(path), pagesize=(W, H), initialFontName=FONT)
    c.setTitle(TITLE)
    c.setAuthor(AUTHOR)

    # 1: title page
    centred(c, "GREAT BRITISH", H - 3.2 * inch, BOLD, 40)
    centred(c, "LARGE PRINT", H - 3.9 * inch, BOLD, 40)
    centred(c, "WORD SEARCH", H - 4.6 * inch, BOLD, 40)
    centred(c, SUBTITLE, H - 5.5 * inch, FONT, 20)
    centred(c, AUTHOR, 2 * inch, FONT, 16)
    c.showPage()
    # 2: copyright
    c.setFont(FONT, 12)
    for i, line in enumerate([f"{TITLE}", f"Copyright © {YEAR} {AUTHOR}. All rights reserved.",
                              "No part of this book may be reproduced without permission,",
                              "except for personal use by the purchaser."]):
        c.drawString(MARGIN, 2.5 * inch - i * 18, line)
    c.showPage()
    # 3: how to play
    centred(c, "How to Play", H - 1.8 * inch, BOLD, 30)
    tips = ["Each puzzle has a theme and a list of 15 words.",
            "Find every word hidden in the grid of letters.",
            "Words run forwards only: left to right, top to bottom,",
            "or diagonally. None are written backwards.",
            "Spaces in the word list are left out of the grid,",
            "so ST HELIER appears in the grid as STHELIER.",
            "Circle each word as you find it and tick it off the list.",
            "Stuck? Solutions start on page " + str(5 + len(puzzles)) + "."]
    c.setFont(FONT, 18)
    for i, t in enumerate(tips):
        c.drawString(MARGIN + 0.2 * inch, H - 2.9 * inch - i * 0.52 * inch, t)
    c.showPage()
    # 4: blank so puzzle 1 starts on a right-hand page
    c.showPage()

    page = 5
    cell = (W - 2 * MARGIN - 0.5 * inch) / SIZE
    for n, (theme, words, display, grid, placed) in enumerate(puzzles, 1):
        centred(c, f"Puzzle {n}", H - MARGIN - 0.1 * inch, FONT, 16)
        centred(c, theme, H - MARGIN - 0.55 * inch, BOLD, 26)
        top = H - MARGIN - 1.05 * inch
        draw_grid(c, grid, (W - SIZE * cell) / 2, top, cell, 21)
        # word list: 3 columns
        c.setFont(FONT, 16)
        y0 = top - SIZE * cell - 0.65 * inch
        colw = (W - 2 * MARGIN) / 3
        for i, wd in enumerate(sorted(display)):
            x, y = MARGIN + (i % 3) * colw + 0.1 * inch, y0 - (i // 3) * 0.33 * inch
            c.setLineWidth(1)
            c.rect(x, y - 1, 11, 11)  # empty tick box
            c.drawString(x + 18, y, wd)
        page_number(c, page)
        c.showPage()
        page += 1

    sol_start = page
    small = 3.3 * inch / SIZE
    per_page = 4
    for s in range(0, len(puzzles), per_page):
        centred(c, "Solutions", H - MARGIN, BOLD, 20)
        for k, (theme, words, display, grid, placed) in enumerate(puzzles[s:s + per_page]):
            n = s + k + 1
            x = MARGIN + 0.1 * inch + (k % 2) * 3.6 * inch
            y = H - MARGIN - 0.75 * inch - (k // 2) * 4.55 * inch
            c.setFont(BOLD, 12)
            c.setFillColor(black)
            c.drawString(x, y + 0.12 * inch, f"{n}. {theme}")
            draw_grid(c, grid, x + 0.1 * inch, y - 0.1 * inch, small, 10, placed)
        page_number(c, page)
        c.showPage()
        page += 1
    if page % 2 == 0:  # finish on an even page count
        c.showPage()
        page += 1
    c.save()
    return path, page - 1, sol_start


def cover(pages):
    """Full-wrap paperback cover: bleed + back + spine + front + bleed (KDP white paper spine = 0.002252in/page)."""
    bleed, spine = 0.125 * inch, pages * 0.002252 * inch
    cw, ch = 2 * bleed + 2 * W + spine, 2 * bleed + H
    path = OUT / "wordsearch-cover.pdf"
    c = canvas.Canvas(str(path), pagesize=(cw, ch), initialFontName=FONT)
    navy, sea, sand = HexColor("#16325c"), HexColor("#2f7fb5"), HexColor("#f3e3b5")
    c.setFillColor(navy)
    c.rect(0, 0, cw, ch, stroke=0, fill=1)
    fx = bleed + W + spine  # front cover left edge
    # front: bunting-style stripe and decorative letter tiles
    c.setFillColor(sea)
    c.rect(fx, ch - bleed - 3.9 * inch, W + bleed, 3.9 * inch + bleed, stroke=0, fill=1)
    for i, (txt, sz, y) in enumerate([("GREAT BRITISH", 44, 1.45), ("LARGE PRINT", 58, 2.35), ("WORD SEARCH", 58, 3.25)]):
        c.setFillColor(white if i else sand)
        c.setFont(BOLD, sz)
        c.drawCentredString(fx + W / 2, ch - bleed - y * inch, txt)
    rnd = random.Random(7)
    tile, word = 0.62 * inch, "SEASIDE"
    gx = fx + (W - 7 * tile) / 2
    for r in range(5):
        for col in range(7):
            x, y = gx + col * tile, ch - bleed - 4.6 * inch - (r + 1) * tile
            hit = r == 2
            c.setFillColor(sand if hit else HexColor("#22467a"))
            c.roundRect(x + 3, y + 3, tile - 6, tile - 6, 6, stroke=0, fill=1)
            c.setFillColor(navy if hit else HexColor("#8fb3de"))
            c.setFont(BOLD, 24)
            c.drawCentredString(x + tile / 2, y + tile * .3, word[col] if hit else rnd.choice("ABCDEFGHIKLMNOPRSTUWY"))
    c.setFillColor(sand)
    c.setFont(BOLD, 22)
    c.drawCentredString(fx + W / 2, bleed + 1.9 * inch, "50 Themed Puzzles for Adults & Seniors")
    c.setFillColor(white)
    c.setFont(FONT, 16)
    c.drawCentredString(fx + W / 2, bleed + 1.4 * inch, "Seaside · Afternoon Tea · Garden Birds · Sunday Roast & more")
    c.drawCentredString(fx + W / 2, bleed + 0.7 * inch, AUTHOR)
    # back cover blurb (barcode area bottom-right left clear for KDP)
    bx = bleed + 0.75 * inch
    c.setFillColor(sand)
    c.setFont(BOLD, 24)
    c.drawString(bx, ch - bleed - 1.4 * inch, "A cuppa and a puzzle.")
    c.setFillColor(white)
    c.setFont(FONT, 15)
    lines = ["Relax with 50 cheerful word searches celebrating everything",
             "we love about Britain — from seaside piers and village fetes",
             "to Sunday roasts, garden birds and proper puddings.",
             "",
             "•  Extra-large, bold letters that are easy on the eyes",
             "•  One puzzle per page with plenty of space",
             "•  Words run forwards only — no backwards words",
             "•  Tick-box word lists and full solutions at the back",
             "",
             "A lovely gift for parents, grandparents and puzzle fans."]
    for i, t in enumerate(lines):
        c.drawString(bx, ch - bleed - 2.1 * inch - i * 0.34 * inch, t)
    if pages >= 80:  # KDP only allows spine text on books with 79+ pages
        c.saveState()
        c.translate(bleed + W + spine / 2, ch / 2)
        c.rotate(-90)
        c.setFont(BOLD, 12)
        c.setFillColor(white)
        c.drawCentredString(0, -4, TITLE.upper())
        c.restoreState()
    c.save()
    return path, cw / inch, ch / inch, spine / inch


def main():
    OUT.mkdir(exist_ok=True)
    rnd = random.Random(2026)
    puzzles = []
    for theme, words in THEMES:
        display = [w.replace("_", " ") for w in words.split()]
        clean = [w.replace("_", "") for w in words.split()]
        assert len(clean) == 15 and max(map(len, clean)) <= SIZE, theme
        assert not [a for a in clean for b in clean if a != b and a in b], (theme, "a word is inside another word")
        grid, placed = make_grid(clean, rnd)
        puzzles.append((theme, clean, display, grid, placed))
    ipath, pages, sol = interior(puzzles)
    cpath, cw, ch, sp = cover(pages)
    print(f"Interior: {ipath} ({pages} pages, solutions from p{sol})")
    print(f"Cover:    {cpath} ({cw:.3f} x {ch:.3f} in, spine {sp:.3f} in)")


if __name__ == "__main__":
    main()
