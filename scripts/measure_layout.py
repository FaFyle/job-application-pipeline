"""Measure a rendered CV page, in centimetres.

Usage:
    python measure_layout.py <png-or-dir> [page_width_cm]

Looking at a render tells you "that looks a bit narrow". Measuring it tells you "the
content band is 19.5cm on a 21cm page, so the right margin is 0.4cm" - which is a
specific, checkable fact you can go and fix. Use both; this is the half that finds
layout bugs.

Reports per page: the content bounding box, all four margins, content width and
height, and a warning when anything reaches the paper edge (which usually means
something will be clipped when printed).

page_width_cm defaults to 21.0 (A4). Pass 21.59 for US Letter.
"""

import sys
import os
import glob

from PIL import Image

# Anything darker than this counts as content. Deliberately close to white so faint
# rules and light grey text still register.
INK_THRESHOLD = 245


def measure(path, page_width_cm):
    img = Image.open(path).convert("L")
    w, h = img.size
    px_per_cm = w / page_width_cm
    page_height_cm = h / px_per_cm

    # Bounding box of everything that isn't paper.
    ink = img.point(lambda p: 255 if p < INK_THRESHOLD else 0)
    bbox = ink.getbbox()

    print("%s  (%dpx x %dpx, %.1f px/cm)" % (os.path.basename(path), w, h, px_per_cm))
    print("  page            %.2f cm x %.2f cm" % (page_width_cm, page_height_cm))

    if not bbox:
        print("  EMPTY PAGE - no content found")
        return

    left, top, right, bottom = bbox
    print("  content box     x %d..%d, y %d..%d px" % (left, right, top, bottom))
    print("  margins         left %.2f  right %.2f  top %.2f  bottom %.2f cm" % (
        left / px_per_cm,
        (w - right) / px_per_cm,
        top / px_per_cm,
        (h - bottom) / px_per_cm,
    ))
    print("  content         %.2f cm wide, %.2f cm tall" % (
        (right - left) / px_per_cm,
        (bottom - top) / px_per_cm,
    ))

    edge = []
    if left <= 1:
        edge.append("left")
    if right >= w - 1:
        edge.append("right")
    if top <= 1:
        edge.append("top")
    if bottom >= h - 1:
        edge.append("bottom")
    if edge:
        print("  WARNING: content touches the %s edge - likely clipped when printed"
              % ", ".join(edge))

    # Widest inked row, which catches a single element overhanging the text block
    # even when the overall box looks sane.
    px = ink.load()
    widest, widest_y = 0, 0
    for y in range(0, h, max(1, h // 400)):  # sample rows; full scan is unnecessary
        row_left, row_right = None, None
        for x in range(w):
            if px[x, y]:
                if row_left is None:
                    row_left = x
                row_right = x
        if row_left is not None and (row_right - row_left) > widest:
            widest, widest_y = row_right - row_left, y
    if widest:
        print("  widest line     %.2f cm (at y=%.2f cm)" % (
            widest / px_per_cm, widest_y / px_per_cm))


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2

    target = os.path.abspath(sys.argv[1])
    page_width_cm = float(sys.argv[2]) if len(sys.argv) > 2 else 21.0

    if os.path.isdir(target):
        paths = sorted(glob.glob(os.path.join(target, "page*.png")))
    else:
        paths = [target]

    if not paths:
        print("ERROR: nothing to measure at %s" % target)
        return 1

    for p in paths:
        measure(p, page_width_cm)
        print("")
    return 0


if __name__ == "__main__":
    sys.exit(main())
