"""Rasterize a PDF to one PNG per page, so the result can actually be looked at.

Usage:
    python pdf_to_png.py <pdf> <out_dir> [dpi]

At the default 110 dpi an A4 page comes out around 910x1287 - large enough to read
body text in, small enough to open quickly.

Old PNGs in the output directory are deleted first. This matters more than it looks:
if a build fails and leaves last run's images behind, the next inspection debugs a
document that no longer exists.
"""

import sys
import glob
import os

try:
    import pymupdf
except ImportError:  # older releases used the fitz name
    import fitz as pymupdf


def main():
    if len(sys.argv) < 3:
        print(__doc__.strip())
        return 2

    pdf_path = os.path.abspath(sys.argv[1])
    out_dir = os.path.abspath(sys.argv[2])
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 110

    if not os.path.exists(pdf_path):
        print("ERROR: no such pdf: %s" % pdf_path)
        return 1

    os.makedirs(out_dir, exist_ok=True)

    # Clear previous renders before writing new ones.
    stale = sorted(glob.glob(os.path.join(out_dir, "page*.png")))
    for f in stale:
        os.remove(f)
    if stale:
        print("cleared %d stale png(s)" % len(stale))

    doc = pymupdf.open(pdf_path)
    written = []
    for i in range(doc.page_count):
        pix = doc[i].get_pixmap(dpi=dpi)
        out = os.path.join(out_dir, "page%d.png" % (i + 1))
        pix.save(out)
        written.append((out, pix.width, pix.height))
    doc.close()

    for path, w, h in written:
        print("PNG=%s (%dx%d)" % (path, w, h))
    print("PAGES=%d" % len(written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
