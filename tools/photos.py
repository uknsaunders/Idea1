#!/usr/bin/env python3
"""Screen personal photos for stock-agency suitability.

Usage:  python3 tools/photos.py <input_dir>          (default: photos/inbox)

Writes (all under photos/, which is git-ignored — never commit personal photos):
  photos/report.csv      one row per image: size, sharpness, exposure, duplicates, location, verdict
  photos/ready/          full-size JPEG copies with ALL metadata (incl. GPS) removed, for upload
  photos/sheets/         numbered contact sheets for visual review
"""
import csv
import math
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageOps

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass

ROOT = pathlib.Path(__file__).resolve().parent.parent / "photos"
EXTS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".tif", ".tiff"}
ADOBE_MIN_MP = 4.0   # Adobe Stock minimum
ALAMY_MIN_MP = 6.0   # Alamy wants ≥17MB uncompressed ≈ 6MP

# Rough bounding boxes for location-based keywording
PLACES = {
    "Jersey": (49.16, 49.27, -2.27, -1.99),
    "Guernsey": (49.40, 49.52, -2.70, -2.49),
}


def gps(img):
    try:
        g = img.getexif().get_ifd(0x8825)
        if not g or 2 not in g or 4 not in g:
            return None

        def deg(v, ref):
            d = float(v[0]) + float(v[1]) / 60 + float(v[2]) / 3600
            return -d if ref in ("S", "W") else d
        return deg(g[2], g.get(1, "N")), deg(g[4], g.get(3, "E"))
    except Exception:
        return None


def place(coord):
    if not coord:
        return ""
    lat, lon = coord
    for name, (a, b, c, d) in PLACES.items():
        if a <= lat <= b and c <= lon <= d:
            return name
    return f"{lat:.3f},{lon:.3f}"


def taken(img):
    try:
        return str(img.getexif().get_ifd(0x8769).get(36867) or img.getexif().get(306) or "")
    except Exception:
        return ""


def metrics(img):
    g = img.convert("L")
    g.thumbnail((1024, 1024))
    a = np.asarray(g, dtype=np.float32)
    # Sharpness: variance of the Laplacian, normalised for a 1024px long edge
    lap = a[1:-1, 1:-1] * -4 + a[:-2, 1:-1] + a[2:, 1:-1] + a[1:-1, :-2] + a[1:-1, 2:]
    sharp = float(lap.var())
    mean = float(a.mean())
    clip_hi = float((a >= 250).mean())
    clip_lo = float((a <= 5).mean())
    # dHash for near-duplicate detection
    h = np.asarray(img.convert("L").resize((9, 8)), dtype=np.int16)
    dhash = int("".join("1" if x else "0" for x in (h[:, 1:] > h[:, :-1]).flatten()), 2)
    return sharp, mean, clip_hi, clip_lo, dhash


def main():
    src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "inbox"
    files = sorted(p for p in src.rglob("*") if p.suffix.lower() in EXTS)
    if not files:
        sys.exit(f"No images found in {src}")
    ready, sheets = ROOT / "ready", ROOT / "sheets"
    ready.mkdir(parents=True, exist_ok=True)
    sheets.mkdir(parents=True, exist_ok=True)

    rows, seen = [], []
    for i, f in enumerate(files, 1):
        try:
            img = Image.open(f)
            coord, when = gps(img), taken(img)
            img = ImageOps.exif_transpose(img).convert("RGB")
        except Exception as e:
            rows.append(dict(id=i, file=f.name, verdict=f"unreadable: {e}"))
            continue
        w, h = img.size
        mp = w * h / 1e6
        sharp, mean, hi, lo, dh = metrics(img)
        problems = []
        if mp < ADOBE_MIN_MP:
            problems.append(f"too small ({mp:.1f}MP)")
        if sharp < 60:
            problems.append("blurry")
        if mean < 45 or lo > 0.25:
            problems.append("too dark")
        if mean > 215 or hi > 0.25:
            problems.append("overexposed")
        # Only compare against photos that passed, so a sharp retake beats an earlier blurry one
        dup = "" if problems else next((s for s, d in seen if bin(d ^ dh).count("1") <= 6), "")
        if dup:
            problems.append(f"near-duplicate of #{dup}")
        elif not problems:
            seen.append((i, dh))
        verdict = "OK" if not problems else "; ".join(problems)

        out = f"{i:03d}.jpg"
        if not problems:
            # Re-encode from pixels only: drops EXIF, GPS, XMP and maker notes entirely
            Image.frombytes("RGB", img.size, img.tobytes()).save(ready / out, "JPEG", quality=95, optimize=True)
        rows.append(dict(id=i, file=f.name, out=out, width=w, height=h, megapixels=round(mp, 1),
                         alamy_ok="yes" if mp >= ALAMY_MIN_MP else "no", sharpness=round(sharp),
                         brightness=round(mean), taken=when, location=place(coord), verdict=verdict))

    with open(ROOT / "report.csv", "w", newline="") as fh:
        cols = ["id", "file", "out", "width", "height", "megapixels", "alamy_ok", "sharpness",
                "brightness", "taken", "location", "verdict"]
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        wr.writerows(rows)

    # Contact sheets: 4x3 grid of numbered thumbnails
    per, cell = 12, 360
    for s in range(math.ceil(len(files) / per)):
        sheet = Image.new("RGB", (cell * 4, cell * 3), "white")
        d = ImageDraw.Draw(sheet)
        for k, f in enumerate(files[s * per:(s + 1) * per]):
            idx = s * per + k + 1
            try:
                t = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
                t.thumbnail((cell - 8, cell - 30))
                x, y = (k % 4) * cell + 4, (k // 4) * cell + 26
                sheet.paste(t, (x, y))
            except Exception:
                pass
            v = rows[idx - 1].get("verdict", "")
            d.text(((k % 4) * cell + 6, (k // 4) * cell + 6), f"#{idx} {'OK' if v == 'OK' else v[:40]}",
                   fill=(0, 120, 60) if v == "OK" else (190, 30, 30))
        sheet.save(sheets / f"sheet-{s + 1:02d}.jpg", quality=85)

    ok = sum(r.get("verdict") == "OK" for r in rows)
    print(f"{len(rows)} images screened, {ok} pass technical checks. "
          f"Report: {ROOT / 'report.csv'}  Sheets: {sheets}")


if __name__ == "__main__":
    main()
